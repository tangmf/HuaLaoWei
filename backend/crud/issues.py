from mobile_app.backend.data_stores.resources import Resources
from mobile_app.backend.models.issues import IssueReport
from psycopg.rows import dict_row

async def get_issues(resources: Resources, params: dict):
    filters, values = [], []

    def add_filter(condition: str, value):
        filters.append(condition.replace("{}", f"${len(values)+1}"))
        values.append(value)

    if params.get("subzoneName"): add_filter("sz.name = {}", params["subzoneName"])
    if params.get("from"): add_filter("i.datetime_updated >= {}", params["from"])
    if params.get("to"): add_filter("i.datetime_updated <= {}", params["to"])
    if params.get("severity"): add_filter("i.severity = {}", params["severity"])
    if params.get("status"): add_filter("i.status = {}", params["status"])

    if params.get("types"):
        types = params["types"].split(",")
        placeholders = ','.join(f"${len(values)+i+1}" for i in range(len(types)))
        filters.append(f"""EXISTS (
            SELECT 1 FROM issue_type_to_issue_mapping itim
            JOIN issue_types it ON itim.issue_type_id = it.issue_type_id
            WHERE itim.issue_id = i.issue_id AND it.name IN ({placeholders})
        )""")
        values.extend(types)

    if params.get("subtypes"):
        subtypes = params["subtypes"].split(",")
        placeholders = ','.join(f"${len(values)+i+1}" for i in range(len(subtypes)))
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
        LIMIT ${len(values)-1} OFFSET ${len(values)}
    """
    async with pool.acquire() as conn:
        return await conn.fetch(query, *values)
    

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
        

async def fetch_issue_subtype(resources: Resources, ):
    async with resources.db_client.acquire() as conn:
        return await conn.fetch("""
            SELECT ist.issue_subtype_id, ist.name, ist.description, ist.issue_type_id
            FROM issue_subtypes ist
            ORDER BY ist.issue_subtype_id
        """)


async def get_issue_type_and_subtype(resources: Resources, ):
    async with resources.db_client.acquire() as conn:
        return await conn.fetch("""
            SELECT it.issue_type_id, it.name AS type_name, it.description AS type_description,
                   ist.issue_subtype_id, ist.name AS subtype_name, ist.description AS subtype_description
            FROM issue_types it
            LEFT JOIN issue_subtypes ist ON it.issue_type_id = ist.issue_type_id
            ORDER BY it.issue_type_id, ist.issue_subtype_id
        """)


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
