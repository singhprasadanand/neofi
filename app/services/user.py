from sqlalchemy.orm import Session
from app.models.user import User, BlacklistedToken
from app.schemas.user import RoleEnum
from app.schemas.auth import RegisterRequest
from app.utils.db_utils.database import get_db
from app.utils.security import password_hash, verify_password, create_access_token, oauth_scheme, decode_access_token
from fastapi import HTTPException, status, Depends
from jose import jwt, JWTError, ExpiredSignatureError


def register_user(db: Session, data: RegisterRequest):
    existing = db.query(User).filter_by(username=data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=password_hash(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user


def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(db, token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter_by(username=username).first()
    if user is None:
        raise credentials_exception
    return user


def require_role(required_role: RoleEnum):
    def role_checker(user: User = Depends(get_current_user)):
        if RoleEnum[user.role.upper()] < required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role",
            )
        return user

    return role_checker


def blacklist_token(db: Session, token: str):
    blacklisted = BlacklistedToken(token=token)
    db.add(blacklisted)
    db.commit()
    return


def verify_token(db: Session, token: str):
    if db.query(BlacklistedToken).filter_by(token=token).first():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been blacklisted")

    try:
        payload = decode_access_token(token)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
