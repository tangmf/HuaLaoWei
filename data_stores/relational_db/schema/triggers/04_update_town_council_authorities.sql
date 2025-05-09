CREATE TRIGGER trg_sync_authorities_from_town_councils
AFTER INSERT OR UPDATE OR DELETE ON town_councils
FOR EACH ROW EXECUTE FUNCTION sync_authorities_from_town_councils();
