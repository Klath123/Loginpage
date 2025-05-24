from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, BackgroundTasks,Request
from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from src.schema.auth import TokenData,CurrentUser,VerifyOtp,ResetPassword
from src.config import Config
import random
from src.db.main import collection
from src.utils.sendEmail import welcome_email


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="profile")  


def generate_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token =  request.cookies.get("token")
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        email = payload.get("sub")
        
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception

    user = collection.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    
    return CurrentUser(
    email=user["email"],
    name=user.get("name", ""),
    isAccountVerified=user.get("verified","")
    )

def is_password_enough(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    if not any(char in "!@#$%^&*()-_=+[]{};:,.<>?/" for char in password):
        return False
    return True

def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=Config.REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt


async def set_verification_otp(
    current_user: CurrentUser,background_tasks: BackgroundTasks
):
    email = current_user.email
    user = collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get("verified") is True:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    otp = f"{random.randint(100000, 999999)}"

    expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    collection.update_one(
        {"email": email},
        {
            "$set": {
                "verifyOtp": otp,
                "verifyExpiry": expiry
            }
        }
    )
    html = f"""
    <html>
        <body>
            <h1>Welcome to our service!</h1>
            <p>Your OTP for email verification is: {otp}</p>
            <p>This OTP is valid for 10 minutes.</p>
        </body>"""
    subject = "Email Verification"
    welcome_email([email],html,subject,background_tasks)
    return {
        "success": True,
        "message": "Verification otp sent"
    }

    
async def verify_otp(
    otp: VerifyOtp,
    background_task: BackgroundTasks,
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
):
    email = current_user.email
    print(email)
    user = collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("verifyOtp") is None or otp.otp != user.get("verifyOtp"):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    expiry = user.get("verifyExpiry")
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP Expired")

    if user.get("verified") is True:
        raise HTTPException(status_code=400, detail="Email already verified")

    collection.update_one(
        {"email": email},
        {
            "$set": {
                "verified": True
            },
            "$unset": {
                "verifyOtp": "",
                "verifyExpiry": ""
            }
        }
    )
    html = """ ... (welcome email HTML) ... """
    subject = "Email verified successfully"
    welcome_email([email], html, subject, background_task)
    return {
        "message": "Email verified successfully",
        "success": True
    }

    
    
async def reset_password_otp(
    current_user: TokenData,background_tasks: BackgroundTasks
):
    email = current_user.email
    user = collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    otp = f"{random.randint(100000, 999999)}"

    expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    collection.update_one(
        {"email": email},
        {
            "$set": {
                "resetOtp": otp,
                "resetExpiry": expiry
            }
        }
    )
    html = f"""
    <html>
        <body>
            <h1>Welcome to our service!</h1>
            <p>Your OTP for password reset is: {otp}</p>
            <p>This OTP is valid for 10 minutes.</p>
        </body>"""
    subject = "password reset"
    welcome_email([email],html,subject,background_tasks)
    return {
        "message": "OTP sent to your email",
        "otp": otp,
        "expiry": expiry
    }

def reset_password(reset: ResetPassword):
    email = reset.email
    otp = reset.otp
    new_password = reset.newPassword
    user =   collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if "resetOtp" not in user or user["resetOtp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if user["resetExpiry"]<datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP Expired")
    
    if not is_password_enough(new_password):
        raise HTTPException(status_code=400,detail="Password not strong enough")
    
    hashed_password = generate_password_hash(new_password)

    collection.update_one(
        {"email": email},
        {
            "$set": {"password": hashed_password},
            "$unset": {"resetOtp": "", "resetExpiry": ""}
        }
    )

    return {"message": "Password reset successful"}


async def get_current_active_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        email = payload.get("sub")
        
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception

    user = collection.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    
    if not user["verified"]:
        raise HTTPException(status_code=400,detail="User not verified")
    
    return CurrentUser(
    email=user["email"],
    name=user.get("name", ""),
    )

def verify_token_from_cookies(request: Request) -> bool:
    token = request.cookies.get("token")

    if not token:
        return False 
    
    payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
    email = payload.get("sub")
    if not email:
       return False
    user = collection.find_one({"email": email})
    if user is None :
       return False
   
    return True
    
async def send_verification_otp(user: dict, background_tasks: BackgroundTasks):
    email = user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    existing_user = collection.find_one({"email": email})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    otp = f"{random.randint(100000, 999999)}"
    expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    collection.update_one(
        {"email": email},
        {
            "$set": {"verificationOtp": otp, "verificationExpiry": expiry}
        }
    )
    # collection.update_one(
    #     {"email": email},
    #     {
    #         "$set": {
    #             "verificationOtp": otp,
    #             "verificationExpiry": expiry,
    #         }
    #     }
    # )
    html = f"""
    <html>
        <body>
            <h1>Verify Your Email Address</h1>
            <p>Your OTP for email verification is: <strong>{otp}</strong></p>
            <p>This OTP is valid for 10 minutes.</p>
            <p>If you did not request this, please ignore this email.</p>
        </body>
    </html>
    """

    subject = "Email Verification OTP"
    welcome_email([email], html, subject, background_tasks)
    return {
        "message": "Verification OTP sent to your email",
        "expiry": expiry
    }


async def verify_otp_login(email: str, otp: str):
    if not email or not otp:
        raise HTTPException(status_code=400, detail="Email and OTP are required")
    
    user = collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    mongootp = user.get("verificationOtp")
    print(mongootp)
    if str(user.get("verificationOtp")) is None or str(otp) != str(user.get("verificationOtp")):
        raise HTTPException(status_code=400, detail="Invalid OTP")
    # if user.get("verificationOtp") is None or str(otp) != str(user.get("verificationOtp")):
    #     raise HTTPException(status_code=400, detail="Invalid OTP")
    # if user.get("verificationOtp") is None or otp != user.get("verificationOtp"):
    #     raise HTTPException(status_code=400, detail="Invalhbid OTP")
   
    expiry = user.get("verificationExpiry")
    if expiry is None:
        raise HTTPException(status_code=400, detail="OTP not set")

    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP Expired")

    # collection.update_one(
    #     {"email": email},
    #     {
    #         "$unset": {"verificationOtp": "", "verificationExpiry": ""}
    #     }
    # )

    return {
        "success": True,
    }
