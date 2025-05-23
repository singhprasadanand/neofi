from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
