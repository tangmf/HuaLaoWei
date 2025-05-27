DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger
    WHERE tgname = 'trg_sync_authorities_from_town_councils'
  ) THEN
    CREATE TRIGGER trg_sync_authorities_from_town_councils
    AFTER INSERT OR UPDATE OR DELETE ON town_councils
    FOR EACH ROW EXECUTE FUNCTION sync_authorities_from_town_councils();
  END IF;
END
$$;
