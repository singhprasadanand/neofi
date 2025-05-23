from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.user import register_user, authenticate_user, blacklist_token, verify_token
from app.utils.security import create_access_token, oauth_scheme
from app.utils.db_utils.database import get_db

auth_router = APIRouter()



@auth_router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, data)
    token = create_access_token({"sub": user.username})
    return {"access_token": token}

@auth_router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    token = create_access_token({"sub": user.username})
    return {"access_token": token}

@auth_router.post("/refresh", response_model=TokenResponse)
def refresh(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):  # token would typically come from Authorization header
    payload = verify_token(db,token)
    new_token = create_access_token({"sub": payload["sub"]})
    return {"access_token": new_token}

@auth_router.post("/logout")
def logout(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    blacklist_token(db, token)
    return {"message": "Successfully logged out"}
