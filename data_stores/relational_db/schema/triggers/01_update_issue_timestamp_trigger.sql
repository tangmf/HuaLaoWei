DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'update_issue_timestamp_trigger'
  ) THEN
    CREATE TRIGGER update_issue_timestamp_trigger
    BEFORE UPDATE ON issues
    FOR EACH ROW
    EXECUTE FUNCTION update_issue_timestamp();
  END IF;
END;
$$;
