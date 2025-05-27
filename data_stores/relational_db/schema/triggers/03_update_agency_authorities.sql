DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger
    WHERE tgname = 'trg_sync_authorities_from_agencies'
  ) THEN
    CREATE TRIGGER trg_sync_authorities_from_agencies
    AFTER INSERT OR UPDATE OR DELETE ON agencies
    FOR EACH ROW EXECUTE FUNCTION sync_authorities_from_agencies();
  END IF;
END
$$;
