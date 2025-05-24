from fastapi import APIRouter, HTTPException, status, Response, Depends, Request,BackgroundTasks
from src.schema.auth import UserIn, UserLogin,CurrentUser,TokenData, ResetPassword
from src.db.main import collection
from src.utils.auth import generate_password_hash, create_access_token, get_current_user, verify_password,is_password_enough,create_refresh_token,set_verification_otp, verify_otp,reset_password_otp,reset_password,get_current_active_user
from src.utils.sendEmail import welcome_email
from datetime import datetime
from typing import Annotated

user_router = APIRouter()

@user_router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "name": current_user.name,
        "email": current_user.email,
        "isVerified": current_user.isAccountVerified
    }