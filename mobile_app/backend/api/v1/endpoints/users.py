from fastapi import APIRouter, Request
from mobile_app.backend.crud import users as crud_users

router = APIRouter()

@router.get("/{user_id}/posts")
async def get_user_posts(user_id: int, request: Request):
    posts = await crud_users.get_user_posts(user_id)
    return posts
