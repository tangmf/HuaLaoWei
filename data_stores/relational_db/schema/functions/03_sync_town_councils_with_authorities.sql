CREATE OR REPLACE FUNCTION sync_authorities_from_town_councils() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO authorities (authority_type, authority_ref_id, name, description)
    VALUES ('town_council', NEW.town_council_id, NEW.name, NEW.description);
  ELSIF TG_OP = 'UPDATE' THEN
    UPDATE authorities
    SET name = NEW.name,
        description = NEW.description
    WHERE authority_type = 'town_council' AND authority_ref_id = OLD.town_council_id;
  ELSIF TG_OP = 'DELETE' THEN
    DELETE FROM authorities
    WHERE authority_type = 'town_council' AND authority_ref_id = OLD.town_council_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;
