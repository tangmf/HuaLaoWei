from dashboard.backend.db.database import pool

async def get_open_issues(params: dict):
    filters, values = [], []
    if params.get("subzoneName"):
        filters.append(f"sz.name = ${len(values)+1}")
        values.append(params["subzoneName"])
    if params.get("from"):
        filters.append(f"i.datetime_updated >= ${len(values)+1}")
        values.append(params["from"])
    if params.get("to"):
        filters.append(f"i.datetime_updated <= ${len(values)+1}")
        values.append(params["to"])
    if params.get("types"):
        types = params["types"].split(",")
        filters.append(f"it.name IN ({','.join(f'${len(values)+i+1}' for i in range(len(types)))})")
        values.extend(types)
    if params.get("subtypes"):
        subtypes = params["subtypes"].split(",")
        filters.append(f"isc.name IN ({','.join(f'${len(values)+i+1}' for i in range(len(subtypes)))})")
        values.extend(subtypes)
    if params.get("severity"):
        filters.append(f"i.severity = ${len(values)+1}")
        values.append(params["severity"])
    where_clause = f"WHERE {' AND '.join(filters)} AND i.status != 'Resolved'" if filters else "WHERE i.status != 'Resolved'"
    offset = (int(params.get("page", 1)) - 1) * int(params.get("limit", 10000))
    limit = int(params.get("limit", 10000))
    query = f"""
        SELECT i.description, i.severity, i.latitude, i.longitude, i.address, i.status, sz.name AS subzone_name,
               i.datetime_reported, i.datetime_acknowledged, i.datetime_closed, i.datetime_updated,
               it.name AS issue_type, isc.name AS issue_subtype, a.name AS agency_name, tc.name AS town_council_name
        FROM issues i
        JOIN subzones sz ON i.subzone_id = sz.subzone_id
        JOIN issue_types it ON i.issue_type_id = it.issue_type_id
        JOIN issue_subtypes isc ON i.issue_subtype_id = isc.issue_subtype_id
        JOIN agencies a ON i.agency_id = a.agency_id
        JOIN town_councils tc ON i.town_council_id = tc.town_council_id
        {where_clause}
        ORDER BY i.datetime_updated DESC
        LIMIT ${len(values)+1} OFFSET ${len(values)+2}
    """
    values.extend([limit, offset])
    async with pool.connection() as conn:
        result = await conn.execute(query, values)
        return await result.fetchall()

async def get_resolved_issues(params: dict):
    same_as_open = await get_open_issues(params)
    return same_as_open  # different WHERE i.status = 'Resolved' will be handled in endpoints layer

async def get_daily_count(subzoneName: str = None, issueTypeName: str = None):
    filters, values = [], []
    if subzoneName:
        filters.append(f"sz.name = ${len(values)+1}")
        values.append(subzoneName)
    if issueTypeName:
        filters.append(f"it.name = ${len(values)+1}")
        values.append(issueTypeName)
    base_where = f"WHERE i.datetime_reported >= (CURRENT_DATE - INTERVAL '20 days') {'AND ' + ' AND '.join(filters) if filters else ''}"
    query = f"""
        SELECT DATE(i.datetime_reported) AS report_date, COUNT(*) AS issue_count
        FROM issues i
        JOIN subzones sz ON i.subzone_id = sz.subzone_id
        JOIN issue_types it ON i.issue_type_id = it.issue_type_id
        {base_where}
        GROUP BY report_date
        ORDER BY report_date ASC
    """
    async with pool.connection() as conn:
        result = await conn.execute(query, values)
        rows = await result.fetchall()
    date_counts = {((await conn.fetchval('SELECT CURRENT_DATE')) - timedelta(days=i)).isoformat(): 0 for i in range(21)}
    for row in rows:
        date_counts[row["report_date"].isoformat()] = row["issue_count"]
    return [{"report_date": date, "issue_count": count} for date, count in sorted(date_counts.items())]
