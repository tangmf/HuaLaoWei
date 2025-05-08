CREATE TABLE IF NOT EXISTS issue_subtype_to_issue_mapping (
    issue_id INTEGER REFERENCES issues(issue_id) ON DELETE CASCADE, 
    issue_subtype_id INTEGER REFERENCES issue_subtypes(issue_subtype_id) ON DELETE CASCADE, 
    PRIMARY KEY (issue_id, issue_subtype_id)
);
