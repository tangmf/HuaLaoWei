from fastapi import APIRouter, Request, Depends
from mobile_app.backend.core.security import verify_token
from mobile_app.backend.crud import posts as crud_posts

router = APIRouter()

@router.post("/{user_id}/like_post/{post_id}")
async def like_post(post_id: int, request: Request, user_id: int = Depends(verify_token)):
    await crud_posts.like_post(user_id, post_id)
    return {"message": "Post liked successfully"}

@router.post("/{user_id}/post/{issue_id}")
async def create_post(issue_id: int, request: Request, user_id: int = Depends(verify_token)):
    await crud_posts.create_post(user_id, issue_id)
    return {"message": "Post created successfully"}

@router.get("/post/{post_id}/likes")
async def get_post_likes(post_id: int, request: Request):
    likes = await crud_posts.count_post_likes(post_id)
    return {"likes": likes}
