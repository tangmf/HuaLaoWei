from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.data_stores.resources import resources  
from backend.api.v1.endpoints import auth, posts, users, comments, issues, chatbot

@asynccontextmanager
async def lifespan(app):
    app.state.resources = resources
    yield
    await resources.db_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/v1/users", tags=["Users"])
app.include_router(posts.router, prefix="/v1/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/v1/comments", tags=["Comments"])
app.include_router(issues.router, prefix="/v1/issues", tags=["Issues"])
app.include_router(chatbot.router, prefix="/v1/ai_models/chatbot", tags=["AI Models - Chatbot"])

