CREATE OR REPLACE FUNCTION update_issue_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.datetime_updated = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_issue_timestamp_trigger
BEFORE UPDATE ON issues
FOR EACH ROW
EXECUTE FUNCTION update_issue_timestamp();
