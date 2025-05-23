from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os

oauth_scheme= OAuth2PasswordBearer(tokenUrl='/login')

pass_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRY = int(os.environ.get("ACCESS_TOKEN_EXPIRY", 30))


def password_hash(password: str) -> str:
    return pass_context.hash(password)


def verify_password(password: str, hash_password: str) -> bool:
    return pass_context.verify(password, hash_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expiry_time = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRY)
    to_encode.update({'exp': expiry_time})
    return jwt.encode(to_encode, algorithm=ALGORITHM, key=SECRET_KEY)


def decode_access_token(token: str):
    return jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)



