CREATE OR REPLACE FUNCTION call_issue_webhook()
RETURNS trigger AS $$
DECLARE
  webhook_url text;
  response json;
BEGIN
  -- Lookup webhook URL from system_config
  SELECT value INTO webhook_url
  FROM system_config
  WHERE key = 'webhook.issue.url';

  IF webhook_url IS NULL OR webhook_url = '' OR webhook_url NOT LIKE 'http%' THEN
    RETURN NEW; -- Skip if URL is missing or invalid
  END IF;

  -- POST JSON payload
  response := http_post(
    webhook_url,
    json_build_object('issue_id', NEW.issue_id)::text,
    'application/json'
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop old trigger if exists
DROP TRIGGER IF EXISTS issue_update_trigger ON issues;

-- Create trigger WITHOUT hardcoded argument
CREATE TRIGGER issue_update_trigger
AFTER INSERT OR UPDATE ON issues
FOR EACH ROW
EXECUTE FUNCTION call_issue_webhook();
