from fastapi import APIRouter, Request
from backend.core.security import create_access_token
from backend.crud import auth as crud_auth

router = APIRouter()

@router.post("/signup")
async def signup(request: Request, user: dict):
    resources = request.app.state.resources
    new_user = await crud_auth.create_user(resources=resources, user=user)
    access_token = create_access_token(data={"sub": new_user["user_id"]})
    return {
        "message": "User created successfully",
        "user_id": new_user["user_id"],
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/signin")
async def signin(request: Request, user: dict):
    resources = request.app.state.resources
    user_data = await crud_auth.authenticate_user(resources=resources, user=user)
    if user_data:
        access_token = create_access_token(data={"sub": user_data["user_id"]})
        return {
            "message": "User signed in successfully",
            "access_token": access_token,
            "token_type": "bearer"
        }
    else:
        return {"message": "Invalid username or password"}
