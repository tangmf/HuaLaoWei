from fastapi import APIRouter, Request, Depends
from backend.models.comments import CommentRequest
from backend.core.security import verify_token
from backend.crud import comments as crud_comments

router = APIRouter()

@router.post("/{user_id}/like_comment/{comment_id}")
async def like_comment(request: Request, comment_id: int, user_id: int = Depends(verify_token)):
    resources = request.app.state.resources
    await crud_comments.like_comment(resources=resources, user_id=user_id, comment_id=comment_id)
    return {"message": "Comment liked successfully"}

@router.post("/{user_id}/post/{post_id}/comment")
async def create_comment(request: Request, post_id: int, comment: CommentRequest, user_id: int = Depends(verify_token)):
    resources = request.app.state.resources
    new_comment = await crud_comments.create_comment(resources=resources, user_id=user_id, post_id=post_id, content=comment.content,parent_comment_id= comment.parent_comment_id)
    return {"message": "Comment created successfully", "comment_id": new_comment["comment_id"]}

@router.get("/comment/{comment_id}/likes")
async def get_comment_likes(request: Request, comment_id: int):
    resources = request.app.state.resources
    likes = await crud_comments.count_comment_likes(resources=resources, comment_id=comment_id)
    return {"likes": likes}
