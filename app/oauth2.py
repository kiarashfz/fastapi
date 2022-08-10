import datetime

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import schemas, models

from fastapi.security.oauth2 import OAuth2PasswordBearer

from app.config import settings
from app.database import get_db
from app.schemas import TokenData
from app.utils import verify_password

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(data: dict):
    data["exp"] = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(access_token: str, auth_exception):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)
        email: str = payload.get("email")
        if not email:
            raise auth_exception
        token_data = schemas.TokenData(email=email)
        return token_data
    except JWTError as error:
        print(error)
        raise auth_exception


def get_user(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return user


def authenticate_user(email: str, password: str, db: Session = Depends(get_db)):
    user = get_user(email, db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    user = get_user(token_data.email, db)
    if user is None:
        raise credentials_exception
    return user
