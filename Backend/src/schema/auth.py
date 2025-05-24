from pydantic import BaseModel,EmailStr

class UserIn(BaseModel):
    name: str 
    email: EmailStr
    password: str
 
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenData(BaseModel):
    email: str


class CurrentUser(BaseModel):
    email: EmailStr
    name: str | None
    isAccountVerified: bool

class VerifyOtp(BaseModel):
    otp: str
    email: EmailStr
 

class ResetPassword(BaseModel):
    otp: str
    email: EmailStr
    newPassword: str