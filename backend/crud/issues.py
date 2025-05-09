from backend.data_stores.resources import Resources
from backend.models.issues import IssueReport
from psycopg.rows import dict_row
from typing import Optional
from datetime import date, timedelta

async def get_issues(resources: Resources, params: dict):
    filters, values = [], []

    def add_filter(condition: str, value):
        filters.append(condition.replace("{}", f"%s"))
        values.append(value)

    if params.get("subzoneName"): add_filter("sz.name = {}", params["subzoneName"])
    if params.get("from"): add_filter("i.datetime_updated >= {}", params["from"])
    if params.get("to"): add_filter("i.datetime_updated <= {}", params["to"])
    if params.get("severity"): add_filter("i.severity = {}", params["severity"])
    if params.get("status"): add_filter("i.status = {}", params["status"])

    if params.get("types"):
        types = params["types"].split(",")
        placeholders = ",".join(["%s"] * len(types))
        filters.append(f"""EXISTS (
            SELECT 1 FROM issue_type_to_issue_mapping itim
            JOIN issue_types it ON itim.issue_type_id = it.issue_type_id
            WHERE itim.issue_id = i.issue_id AND it.name IN ({placeholders})
        )""")
        values.extend(types)

    if params.get("subtypes"):
        subtypes = params["subtypes"].split(",")
        placeholders = ",".join(["%s"] * len(subtypes))
        filters.append(f"""EXISTS (
            SELECT 1 FROM issue_subtype_to_issue_mapping iscm
            JOIN issue_subtypes isc ON iscm.issue_subtype_id = isc.issue_subtype_id
            WHERE iscm.issue_id = i.issue_id AND isc.name IN ({placeholders})
        )""")
        values.extend(subtypes)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    offset = (int(params.get("page", 1)) - 1) * int(params.get("limit", 10000))
    limit = int(params.get("limit", 10000))
    values.extend([limit, offset])

    query = f"""
        SELECT i.issue_id, i.description, i.severity, i.latitude, i.longitude, i.address, i.status,
               sz.name AS subzone_name, i.datetime_reported, i.datetime_acknowledged,
               i.datetime_closed, i.datetime_updated,
               COALESCE(json_agg(DISTINCT it.name) FILTER (WHERE it.name IS NOT NULL), '[]') AS issue_types,
               COALESCE(json_agg(DISTINCT isc.name) FILTER (WHERE isc.name IS NOT NULL), '[]') AS issue_subtypes,
               auth.name AS authority_name,
               auth.authority_type,
               auth.authority_ref_id
        FROM issues i
        JOIN subzones sz ON i.subzone_id = sz.subzone_id
        LEFT JOIN issue_type_to_issue_mapping itim ON i.issue_id = itim.issue_id
        LEFT JOIN issue_types it ON itim.issue_type_id = it.issue_type_id
        LEFT JOIN issue_subtype_to_issue_mapping iscm ON i.issue_id = iscm.issue_id
        LEFT JOIN issue_subtypes isc ON iscm.issue_subtype_id = isc.issue_subtype_id
        LEFT JOIN authorities auth ON i.authority_id = auth.authority_id
        {where_clause}
        GROUP BY i.issue_id, sz.name, auth.name, auth.authority_type, auth.authority_ref_id
        ORDER BY i.datetime_updated DESC
        LIMIT %s OFFSET %s
    """

    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, values)
            return await cur.fetchall()
    

async def fetch_issue_type_info_from_name(resources: Resources, name: str) -> int | None:
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM issue_types WHERE name = %s",
                (name,)
            )
            return await cur.fetchone()
    

async def fetch_issue_subtype_info_from_name(resources: Resources, name: str) -> int | None:
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM issue_subtypes WHERE name = %s",
                (name,)
            )
            return await cur.fetchone()
        

async def get_issue_type_and_subtype(resources: Resources, params: dict):
    category = params.get("category", "both")

    query = {
        "type": """
            SELECT issue_type_id, name AS type_name, description AS type_description
            FROM issue_types
            ORDER BY issue_type_id
        """,
        "subtype": """
            SELECT ist.issue_subtype_id, ist.name AS subtype_name, ist.description AS subtype_description,
                   ist.issue_type_id, it.name AS parent_type_name
            FROM issue_subtypes ist
            LEFT JOIN issue_types it ON ist.issue_type_id = it.issue_type_id
            ORDER BY ist.issue_type_id, ist.issue_subtype_id
        """,
        "both": """
            SELECT it.issue_type_id, it.name AS type_name, it.description AS type_description,
                   ist.issue_subtype_id, ist.name AS subtype_name, ist.description AS subtype_description
            FROM issue_types it
            LEFT JOIN issue_subtypes ist ON it.issue_type_id = ist.issue_type_id
            ORDER BY it.issue_type_id, ist.issue_subtype_id
        """
    }.get(category, query := None)

    if query is None:
        raise ValueError("Invalid category value. Must be one of: 'type', 'subtype', or 'both'.")

    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query)
            return await cur.fetchall()


async def get_issues_nearby(resources: Resources, lat: float, lon: float, radius: int):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT 
                    i.*, 
                    fp.*, 
                    c.comment_id, 
                    c.parent_comment_id, 
                    c.content AS comment_content, 
                    c.created_at AS comment_created_at, 
                    COUNT(DISTINCT pv.user_id) AS post_likes, 
                    COUNT(DISTINCT c.comment_id) OVER (PARTITION BY fp.post_id) AS comment_count, 
                    COUNT(DISTINCT cv.user_id) AS comment_likes
                FROM issues i
                LEFT JOIN forum_posts fp ON i.issue_id = fp.issue_id
                LEFT JOIN comments c ON fp.post_id = c.post_id
                LEFT JOIN post_votes pv ON fp.post_id = pv.post_id
                LEFT JOIN comment_votes cv ON c.comment_id = cv.comment_id
                WHERE ST_DWithin(i.location, ST_MakePoint(%s, %s)::geography, %s)
                ORDER BY i.issue_id, fp.post_id, c.comment_id
                """,
                (lon, lat, radius)
            )
            rows = await cur.fetchall()
            return rows


async def create_issue(resources: Resources, issue: IssueReport):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO issues (
                    userid, latitude, longitude, address, description,
                    severity, status, datetime_reported, datetime_updated,
                    authority_id, subzone_id, planning_area_id, is_public
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING issue_id
                """,
                (
                    issue["userid"], issue["latitude"], issue["longitude"], issue["address"],
                    issue["description"], issue["severity"], issue.get("status", "Reported"),
                    issue.get("datetime_reported"), issue.get("datetime_updated"), issue.get("authority_id"), 
                    issue.get("subzone_id"), issue.get("planning_area_id"), issue.get("is_public", True)
                )
            )

            inserted_issue = await cur.fetchone()
            issue_id = inserted_issue["issue_id"]

            if "issue_type_ids" in issue:
                await cur.executemany(
                    "INSERT INTO issue_type_to_issue_mapping (issue_id, issue_type_id) VALUES (%s, %s)",
                    [(issue_id, type_id) for type_id in issue["issue_type_ids"]]
                )

            if "issue_subtype_ids" in issue:
                await cur.executemany(
                    "INSERT INTO issue_subtype_to_issue_mapping (issue_id, issue_subtype_id) VALUES (%s, %s)",
                    [(issue_id, subtype_id) for subtype_id in issue["issue_subtype_ids"]]
                )

            return {"issue_id": issue_id}


async def get_daily_issue_counts_by_subzone(
    resources: Resources,
    days: int,
    issue_types: Optional[list[str]] = None,
    issue_subtypes: Optional[list[str]] = None,
    authority_name: Optional[str] = None,
    subzone_name: Optional[str] = None
):
    today = date.today()
    start_date = today - timedelta(days=days - 1)

    filters = ["i.datetime_reported::date >= %s"]
    values = [start_date]

    if issue_types:
        placeholders = ','.join(['%s'] * len(issue_types))
        filters.append(f"""EXISTS (
            SELECT 1 FROM issue_type_to_issue_mapping itim
            JOIN issue_types it ON itim.issue_type_id = it.issue_type_id
            WHERE itim.issue_id = i.issue_id AND it.name IN ({placeholders})
        )""")
        values.extend(issue_types)

    if issue_subtypes:
        placeholders = ','.join(['%s'] * len(issue_subtypes))
        filters.append(f"""EXISTS (
            SELECT 1 FROM issue_subtype_to_issue_mapping iscm
            JOIN issue_subtypes isc ON iscm.issue_subtype_id = isc.issue_subtype_id
            WHERE iscm.issue_id = i.issue_id AND isc.name IN ({placeholders})
        )""")
        values.extend(issue_subtypes)

    if authority_name:
        filters.append("auth.name = %s")
        values.append(authority_name)

    if subzone_name:
        filters.append("sz.name = %s")
        values.append(subzone_name)

    where_clause = "WHERE " + " AND ".join(filters)

    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                f"""
                SELECT 
                    i.datetime_reported::date AS date, 
                    COUNT(*) AS count
                FROM issues i
                LEFT JOIN authorities auth ON i.authority_id = auth.authority_id
                LEFT JOIN subzones sz ON i.subzone_id = sz.subzone_id
                {where_clause}
                GROUP BY date
                ORDER BY date DESC
                """,
                tuple(values)
            )
            rows = await cur.fetchall()

    # Fill missing dates with 0
    result_map = {row["date"]: row["count"] for row in rows}
    result = []
    for i in range(days):
        day = today - timedelta(days=i)
        result.append({
            "date": day.isoformat(),
            "count": result_map.get(day, 0)
        })

    return result

