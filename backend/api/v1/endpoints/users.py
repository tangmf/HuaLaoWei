from fastapi import APIRouter, Request
from backend.crud import users as crud_users

router = APIRouter()

@router.get("/{user_id}/posts")
async def get_user_posts(request: Request, user_id: int):
    resources = request.app.state.resources
    posts = await crud_users.get_user_posts(resources=resources, user_id=user_id)
    return posts
