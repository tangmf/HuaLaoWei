CREATE OR REPLACE FUNCTION sync_authorities_from_agencies() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO authorities (authority_type, authority_ref_id, name, description)
    VALUES ('agency', NEW.agency_id, NEW.name, NEW.description);
  ELSIF TG_OP = 'UPDATE' THEN
    UPDATE authorities
    SET name = NEW.name,
        description = NEW.description
    WHERE authority_type = 'agency' AND authority_ref_id = OLD.agency_id;
  ELSIF TG_OP = 'DELETE' THEN
    DELETE FROM authorities
    WHERE authority_type = 'agency' AND authority_ref_id = OLD.agency_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;
