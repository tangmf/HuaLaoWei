def format_issue_types_and_subtypes(rows):
    result = {}
    for row in rows:
        type_id = row["issue_type_id"]
        if type_id not in result:
            result[type_id] = {
                "issue_type_id": type_id,
                "name": row["type_name"],
                "description": row["type_description"],
                "subtypes": []
            }
        if row["issue_subtype_id"]:
            result[type_id]["subtypes"].append({
                "issue_subtype_id": row["issue_subtype_id"],
                "name": row["subtype_name"],
                "description": row["subtype_description"]
            })
    return list(result.values())