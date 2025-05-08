CREATE TABLE IF NOT EXISTS issue_cat_to_body_mappings (
    mapping_id SERIAL PRIMARY KEY,
    issue_type_id INTEGER REFERENCES issue_types(issue_type_id),
    issue_subtype_id INTEGER REFERENCES issue_subtypes(issue_subtype_id),
    jurisdiction_id INTEGER REFERENCES jurisdictions(jurisdiction_id),
    responsible_agency_id INTEGER REFERENCES agencies(agency_id),
    responsible_council_id INTEGER REFERENCES town_councils(town_council_id)
);
