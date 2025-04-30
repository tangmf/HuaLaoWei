
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
    # URL-encode the password in case it contains special characters
    pw_enc = quote_plus(pw)
    return f"postgresql://{user}:{pw_enc}@{host}:{port}/{db}"

def connect_to_db():
    dsn = get_database_url()
    # psycopg.connect accepts a PostgreSQL URL directly
    conn = psycopg.connect(dsn)
    return conn


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
            return {"message": "User created successfully", "user_id": new_user["user_id"]}
        

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


