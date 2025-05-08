from fastapi import FastAPI
from app.db.database import lifespan
from app.api.v1.endpoints import auth, users, posts, comments, issues, chatbot

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/v1/users", tags=["Users"])
app.include_router(posts.router, prefix="/v1/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/v1/comments", tags=["Comments"])
app.include_router(issues.router, prefix="/v1/issues", tags=["Issues"])

app.include_router(chatbot.router, prefix="/v1/ai_models/chatbot", tags=["AI Models - Chatbot"])

