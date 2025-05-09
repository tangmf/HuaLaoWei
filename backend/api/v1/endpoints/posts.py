from fastapi import APIRouter, Request, Depends
from mobile_app.backend.core.security import verify_token
from mobile_app.backend.crud import posts as crud_posts

router = APIRouter()

@router.post("/{user_id}/like_post/{post_id}")
async def like_post(request: Request, post_id: int, user_id: int = Depends(verify_token)):
    resources = request.app.state.resources
    await crud_posts.like_post(resources=resources, user_id=user_id, post_id=post_id)
    return {"message": "Post liked successfully"}

@router.post("/{user_id}/post/{issue_id}")
async def create_post(request: Request, issue_id: int, user_id: int = Depends(verify_token)):
    resources = request.app.state.resources
    await crud_posts.create_post(resources=resources, user_id=user_id, issue_id=issue_id)
    return {"message": "Post created successfully"}

@router.get("/post/{post_id}/likes")
async def get_post_likes(request: Request, post_id: int):
    resources = request.app.state.resources
    likes = await crud_posts.count_post_likes(resources=resources, post_id=post_id)
    return {"likes": likes}
