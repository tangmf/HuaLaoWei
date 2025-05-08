DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_proc WHERE proname = 'update_issue_timestamp'
  ) THEN
    CREATE OR REPLACE FUNCTION update_issue_timestamp()
    RETURNS TRIGGER AS $func$
    BEGIN
      NEW.datetime_updated = CURRENT_TIMESTAMP;
      RETURN NEW;
    END;
    $func$ LANGUAGE plpgsql;
  END IF;
END;
$$;
