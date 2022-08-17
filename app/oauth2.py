import datetime

from fastapi import Depends, HTTPException, status, Security
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import schemas, models

from fastapi.security.oauth2 import OAuth2PasswordBearer

from app.config import settings
from app.database import get_db
from app.schemas import TokenData
from app.utils import verify_password
from fastapi.security.api_key import APIKeyHeader

API_KEY = settings.api_key
API_KEY_NAME = settings.api_key_name
api_key_header = APIKeyHeader(name=settings.api_key_name, auto_error=False)


async def get_api_key(header_api_key: str = Security(api_key_header)):
    if header_api_key == settings.api_key:
        return header_api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(data: dict):
    data["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(access_token: str, auth_exception):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)
        user_id: str = payload.get("user_id")
        if not user_id:
            raise auth_exception
        token_data = schemas.TokenDataUserId(user_id=user_id)
        return token_data
    except JWTError as error:
        print(error)
        raise auth_exception


def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return user


def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return user


def authenticate_user(email: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_email(email, db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    return token_data.user_id


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    user = get_user(token_data.user_id, db)
    if user is None:
        raise credentials_exception
    return user


"""wrong api key logic"""
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# api_keys = [
#     settings.api_key
# ]  # This is encrypted in the database

#
# def api_key_auth(api_key: str = Depends(oauth2_scheme)):
#     if api_key not in api_keys:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Forbidden"
#         )
