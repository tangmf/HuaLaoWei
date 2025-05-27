from fastapi import APIRouter, Request, Depends, Query
from backend.core.security import verify_token
from backend.crud import posts as crud_posts

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

@router.get("/forum-posts")
async def get_forum_posts(request: Request, lat: float, lon: float):
    resources = request.app.state.resources

    posts = await crud_posts.get_forum_posts(resources=resources, user_lat=lat, user_lon=lon, radius_meters=2000)

    formatted_posts = [
        {
            "id": post["post_id"],
            "title": post["title"],
            "description": post["description"],
            "latitude": post["latitude"],
            "longitude": post["longitude"],
            "severity": post["severity"],
            "status": post["status"],
            "created_at": post["created_at"],
            "image": f"/{post['file_path']}" if post["file_path"] else None
        }
        for post in posts
    ]
    print(formatted_posts[0]["image"])
    return {"posts": formatted_posts}