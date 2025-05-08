CREATE TABLE IF NOT EXISTS issue_type_to_issue_mapping (
    issue_id INTEGER REFERENCES issues(issue_id) ON DELETE CASCADE, 
    issue_type_id INTEGER REFERENCES issue_types(issue_type_id) ON DELETE CASCADE, 
    PRIMARY KEY (issue_id, issue_type_id)
);
