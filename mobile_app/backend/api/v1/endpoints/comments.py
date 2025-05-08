from fastapi import APIRouter, Request, Depends
from mobile_app.backend.models.comment_request import CommentRequest
from mobile_app.backend.core.security import verify_token
from mobile_app.backend.crud import comments as crud_comments

router = APIRouter()

@router.post("/{user_id}/like_comment/{comment_id}")
async def like_comment(comment_id: int, request: Request, user_id: int = Depends(verify_token)):
    await crud_comments.like_comment(user_id, comment_id)
    return {"message": "Comment liked successfully"}

@router.post("/{user_id}/post/{post_id}/comment")
async def create_comment(post_id: int, comment: CommentRequest, request: Request, user_id: int = Depends(verify_token)):
    new_comment = await crud_comments.create_comment(user_id, post_id, comment.content, comment.parent_comment_id)
    return {"message": "Comment created successfully", "comment_id": new_comment["comment_id"]}

@router.get("/comment/{comment_id}/likes")
async def get_comment_likes(comment_id: int, request: Request):
    likes = await crud_comments.count_comment_likes(comment_id)
    return {"likes": likes}
