CREATE TRIGGER trg_sync_authorities_from_agencies
AFTER INSERT OR UPDATE OR DELETE ON agencies
FOR EACH ROW EXECUTE FUNCTION sync_authorities_from_agencies();
