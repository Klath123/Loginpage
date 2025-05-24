from fastapi import APIRouter, HTTPException, status, Response, Depends, Request,BackgroundTasks
from src.schema.auth import UserIn, UserLogin,CurrentUser,TokenData, ResetPassword,VerifyOtp
from src.db.main import collection
from src.utils.auth import generate_password_hash, create_access_token, get_current_user, verify_password,is_password_enough,create_refresh_token,set_verification_otp, verify_otp,reset_password_otp,reset_password,verify_token_from_cookies,send_verification_otp,verify_otp_login
from src.utils.sendEmail import welcome_email
from datetime import datetime
from typing import Annotated
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

                          
auth_router = APIRouter() 

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(user: UserIn, response: Response, background_tasks: BackgroundTasks):
    existing = collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if len(user.email) < 1:
        raise HTTPException(status_code=400, detail="Email is required")
    if len(user.name) < 1:
        raise HTTPException(status_code=400, detail="Name is required")
    
    if is_password_enough(user.password) == False:
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character")
    

    hashed_password = generate_password_hash(user.password)
    collection.insert_one({
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "verified": False,
        "createdAt":  datetime.utcnow() 
    })

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    response.set_cookie(key="token", value=access_token, httponly=True, secure=False, samesite="strict",max_age=60*60*30)
    response.set_cookie(key="refresh", value=refresh_token, httponly=True, secure=False, samesite="strict",max_age=60*60*24*7)
    # Send a welcome email
    html = """
    <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Welcome to Our Platform</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f4f4f4;
      margin: 0;
      padding: 0;
    }
    .container {
      background-color: #ffffff;
      margin: 50px auto;
      padding: 30px;
      max-width: 600px;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    h1 {
      color: #333333;
    }
    p {
      color: #555555;
      line-height: 1.6;
    }
    .button {
      display: inline-block;
      padding: 10px 20px;
      margin-top: 20px;
      background-color: #4CAF50;
      color: #ffffff;
      text-decoration: none;
      border-radius: 5px;
    }
    .footer {
      margin-top: 30px;
      font-size: 12px;
      color: #aaaaaa;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Welcome to Our Platform!</h1>
    <p>Hi there,</p>
    <p>Thank you for registering with us. We're excited to have you on board.</p>
    <p>To get started, please verify your email address by clicking the button below:</p>
    <p>If you have any questions or need assistance, feel free to reply to this email.</p>
    <div class="footer">
      &copy; 2025 Your Company Name. All rights reserved.
    </div>
  </div>
</body>
</html>
"""
    subject = "welcome to our platform"
    welcome_email([user.email],html,subject,background_tasks)
    return {"success": True, "message": "User registered successfully"}


@auth_router.post("/login", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def login(user: UserLogin, response: Response,background_tasks: BackgroundTasks):

    if len(user.email) < 1:
        raise HTTPException(status_code=400, detail="Email is required")
    if len(user.password) < 1:
        raise HTTPException(status_code=400, detail="password is required")
    
    existing = collection.find_one({"email": user.email})
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(user.password, existing["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    await send_verification_otp({"email": user.email}, background_tasks)
    return {"success": True, "message": "OTP sent to your email. Please verify to login."}
    # access_token = create_access_token(data={"sub": user.email})
    # refresh_token = create_refresh_token(data={"sub": user.email})
    # response.set_cookie(key="token", value=access_token, httponly=True, secure=False, samesite="strict",max_age=60*30*60)
    # response.set_cookie(key="refresh", value=refresh_token, httponly=True, secure=False, samesite="strict",max_age=60*60*24*7)
    # return {
    #     "access_token": access_token,
    #     "token_type": "bearer"
    # }

@auth_router.get("/logout",status_code=status.HTTP_200_OK)
async def logout(response: Response):
    response.delete_cookie(key="token")
    response.delete_cookie(key="refresh")
    return {"success": True}

@auth_router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    email = get_current_user(refresh_token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token({"sub": email["email"]})

    # Reset access token cookie
    response.set_cookie(
        key="token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="strict",
        max_age= 60*60*30 # 30 mins
    )

    return {"message": "Access token refreshed"}
 
@auth_router.get("/send-email")
@limiter.limit("5/minute")
async def send(background_tasks: BackgroundTasks,current_user: dict = Depends(get_current_user)):
    no = await set_verification_otp(current_user,background_tasks) 
    return no

@auth_router.post("/verify-email")
@limiter.limit("20/minute")
async def verify(valid: VerifyOtp,background_task:BackgroundTasks,current_user: dict =  Depends(get_current_user)):
    no = await verify_otp(valid,background_task,current_user) 
    return no

@auth_router.post("/send-password")
@limiter.limit("5/minute")
async def reset(current_user: TokenData,background_task:BackgroundTasks):
    no = await reset_password_otp(current_user,background_task)
    return no

@auth_router.get("/is-auth")
async def getAuth(request: Request):
    is_authenticated = verify_token_from_cookies(request)
    return {
            "auth": is_authenticated
        }

@auth_router.post("/reset-password")
async def new(new_password: ResetPassword):
    new =  reset_password(new_password)
    return new

@auth_router.post("/verify-login-otp")
@limiter.limit("5/minute")
async def verify_login_otp(otp_data: VerifyOtp, response: Response):
    current_email = otp_data.email
    current_otp = otp_data.otp
    verified = await verify_otp_login(current_email,current_otp)
    if not verified.get("success"):
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")
    
    access_token = create_access_token(data={"sub": otp_data.email})
    refresh_token = create_refresh_token(data={"sub": otp_data.email})

    response.set_cookie(key="token", value=access_token, httponly=True, secure=False, samesite="strict", max_age=60*30*60)
    response.set_cookie(key="refresh", value=refresh_token, httponly=True, secure=False, samesite="strict", max_age=60*60*24*7)

    return {"success": True, "message": "Login successful"}