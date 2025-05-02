
from fastapi import FastAPI, File, UploadFile, Request, Depends, HTTPException
from pydantic import BaseModel, validator
from typing import Optional, List
from PIL import Image
import io, json
import os
import psycopg
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from contextlib import asynccontextmanager
from urllib.parse import quote_plus
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv  import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Secret key for signing JWTs (keep this secure!)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Token expiration time


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.now(datetime.timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_database_url() -> str:
    user = os.getenv("DB_USER", "")
    pw   = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db   = os.getenv("DB_NAME", "")
    print(f"Connecting to database at {host}:{port} as {user}")
    # URL-encode the password in case it contains special characters
    pw_enc = quote_plus(pw)
    return f"postgresql://{user}:{pw_enc}@{host}:{port}/{db}"

def connect_to_db():
    dsn = get_database_url()
    # psycopg.connect accepts a PostgreSQL URL directly
    conn = psycopg.connect(dsn)
    return conn


class Coordinates(BaseModel):
    lat: float
    lon: float

    @validator('lat')
    def validate_latitude(cls, v):
        if not isinstance(v, float):
            raise TypeError('Latitude must be a float')
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v

    @validator('lon')
    def validate_longitude(cls, v):
        if not isinstance(v, float):
            raise TypeError('Longitude must be a float')
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v


@asynccontextmanager
async def lifespan(app: FastAPI):
    dsn = get_database_url()
    app.state.pool = AsyncConnectionPool(conninfo=dsn)
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

# get user post by userID
@app.get("/user/{user_id}/posts")
async def get_user_posts(user_id: int, request: Request):
    async with request.app.state.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM forum_posts WHERE user_id = %s",
                (user_id,)
            )
            posts = await cur.fetchall()
            return posts
        

# post user like post
@app.post("/user/{user_id}/like_post/{post_id}")
async def post_user_like_post(post_id: int, request: Request, user_id: int = Depends(verify_token)):
    async with request.app.state.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO post_votes (user_id, post_id) VALUES (%s, %s)",
                (user_id, post_id)
            )
            return {"message": "Post liked successfully"}
            

# post user like comment
@app.post("/user/{user_id}/like_comment/{comment_id}")
async def post_user_like_comment(comment_id: int, request: Request, user_id: int = Depends(verify_token)):
    async with request.app.state.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO comment_votes (user_id, comment_id) VALUES (%s, %s)",
                (user_id, comment_id)
            )
            return {"message": "Comment liked successfully"}
        

# get post likes by postID
@app.get("/post/{post_id}/likes")
async def get_post_likes(post_id: int, request: Request):
    async with request.app.state.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT COUNT(*) FROM post_votes WHERE post_id = %s",
                (post_id,)
            )
            likes = await cur.fetchone() 
            return likes["count"]


# get comment likes by commentID
@app.get("/comment/{comment_id}/likes")
async def get_comment_likes(comment_id: int, request: Request):
    async with request.app.state.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT COUNT(*) FROM comment_votes WHERE comment_id = %s",
                (comment_id,)
            )
            likes = await cur.fetchone() 
            return likes["count"]


# post new post
@app.post("/user/{user_id}/post/{issue_id}")
async def post_user_post(issue_id: int, request: Request, user_id: int = Depends(verify_token)):
    async with request.app.state.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO forum_posts (user_id, issue_id) VALUES (%s, %s)",
                (user_id, issue_id)
            )
            return {"message": "Post created successfully"}


# Define the request body model
class CommentRequest(BaseModel):
    content: str
    parent_comment_id: Optional[int] = None  # Optional for replies

# post new comment
@app.post("/user/{user_id}/post/{post_id}/comment")
async def post_user_comment(
    post_id: int, request: Request, comment: CommentRequest, user_id: int = Depends(verify_token)
):
    async with request.app.state.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            # Insert the comment into the database
            await cur.execute(
                """
                INSERT INTO comments (user_id, post_id, parent_comment_id, content)
                VALUES (%s, %s, %s, %s)
                RETURNING comment_id
                """,
                (str(user_id), str(post_id), str(comment.parent_comment_id) if comment.parent_comment_id else None, comment.content)
            )
            new_comment = await cur.fetchone()
            return {"message": "Comment created successfully", "comment_id": new_comment["comment_id"]}
        

# create new user
@app.post("/user")
async def create_user(user: dict, request: Request):
    async with request.app.state.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s) RETURNING user_id",
                (user["username"], user["email"], user["password_hash"])
            )
            new_user = await cur.fetchone()
            # Create a JWT token
            access_token = create_access_token(
                data={"sub": new_user["user_id"]}
            )
            # Return the new user ID and token
            return {"message": "User created successfully", "user_id": new_user["user_id"], "access_token": access_token, "token_type": "bearer"}
        

@app.post("/user/signin")
async def user_signin(user: dict, request: Request):
    async with request.app.state.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            # Check if the user exists and the password matches
            await cur.execute(
                "SELECT * FROM users WHERE username = %s AND password_hash = %s",
                (user["username"], user["password_hash"])
            )
            user_data = await cur.fetchone()
            if user_data:
                # Create a JWT token
                access_token = create_access_token(
                    data={"sub": user_data["user_id"]}
                )
                return {
                    "message": "User signed in successfully",
                    "access_token": access_token,
                    "token_type": "bearer"
                }
            else:
                return {"message": "Invalid username or password"}


# get issues around a radius of coords
@app.get("/issues")
async def get_issues(lat: float, lon: float, request: Request, radius: int = 100):
    async with request.app.state.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                # join forum posts wtih issues to get the issues around a radius of coords. Join fourm posts with comments to get the comments for each post and also be able to view the amount of likes under those comments.
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
                ORDER BY i.issue_id, fp.post_id, c.comment_id;
                """,
                (lon, lat, radius)
            )
            rows = await cur.fetchall()

    # Consolidate results into the desired structure
    issues = {}
    for row in rows:
        issue_id = row["issue_id"]

        # Initialize issue if not already added
        if issue_id not in issues:
            issues[issue_id] = {
                "issue_id": row["issue_id"],
                "user_id": row["user_id"],
                "issue_type_id": row["issue_type_id"],
                "issue_subcategory_id": row["issue_subcategory_id"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "full_address": row["full_address"],
                "location": row["location"],
                "description": row["description"],
                "severity": row["severity"],
                "status": row["status"],
                "datetime_reported": row["datetime_reported"],
                "datetime_acknowledged": row["datetime_acknowledged"],
                "datetime_closed": row["datetime_closed"],
                "datetime_updated": row["datetime_updated"],
                "agency_id": row["agency_id"],
                "town_council_id": row["town_council_id"],
                "subzone_id": row["subzone_id"],
                "planning_area_id": row["planning_area_id"],
                "is_public": row["is_public"],
                "post_id": row["post_id"],
                "created_at": row["created_at"],
                "comments": [],
                "comment_count": row["comment_count"],
                "post_likes": row["post_likes"],
            }

        # Add comment to the post
        if row["comment_id"]:
            issues[issue_id]["comments"].append({
                "comment_id": row["comment_id"],
                "parent_comment_id": row["parent_comment_id"],
                "content": row["comment_content"],
                "comment_created_at": row["comment_created_at"],
                "comment_likes": row["comment_likes"],
            })

    # Convert issues dictionary to a list
    return list(issues.values())


# create new issue
@app.post("/issue")
async def create_issue(issue: dict, request: Request):
    async with request.app.state.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            # retrieve agency_id, town_council_id, subzone_id, planning_area_id based on latitude and longitude
            await cur.execute(
                """
                SELECT 
                    a.agency_id, 
                    tc.town_council_id, 
                    sz.subzone_id, 
                    pa.planning_area_id
                FROM jurisdictions j
                LEFT JOIN agencies a ON j.town_council_id = a.agency_id
                LEFT JOIN town_councils tc ON j.town_council_id = tc.town_council_id
                LEFT JOIN subzones sz ON ST_Intersects(j.geom, sz.geom)
                LEFT JOIN planning_areas pa ON sz.planning_area_id = pa.planning_area_id
                WHERE ST_DWithin(j.geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326), 1000)
                LIMIT 1;
                """,
                (issue["latitude"], issue["longitude"])
            )
            location_data = await cur.fetchone()

            if not location_data:
                raise HTTPException(status_code=404, detail="No jurisdiction found for the given location.")

            # Insert the issue into the database
            await cur.execute(
                """
                INSERT INTO issues (issue_type_id, issue_subcategory_id, latitude, longitude, full_address, location, description, severity, status, datetime_reported, datetime_acknowledged, datetime_closed, datetime_updated, agency_id, town_council_id, subzone_id, planning_area_id, is_public)
                VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING issue_id
                """,
                (issue["issue_type_id"], issue["issue_subcategory_id"], issue["latitude"], issue["longitude"], issue["full_address"], issue["latitude"], issue["longitude"], issue["description"], issue["severity"], issue["status"], issue["datetime_reported"], None, None, None, location_data["agency_id"], location_data["town_council_id"], location_data["subzone_id"], location_data["planning_area_id"], issue["is_public"])
            )
            new_issue = await cur.fetchone()
            return {"message": "Issue created successfully", "issue_id": new_issue["issue_id"]}
        

