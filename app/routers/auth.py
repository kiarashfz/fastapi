from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.oauth2 import create_access_token, authenticate_user
from app.utils import verify_password

from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import schemas

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login")
async def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    searched_user = db.query(models.User).filter(models.User.email == user.username).first()
    if not searched_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid email or password!")
    elif not verify_password(user.password, searched_user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid email or password!")
    else:
        access_token = create_access_token({"email": searched_user.email})
        return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # TODO: inja niaz nabud usero az db brgiri chon nemikhasti returnesh koni ke, hamun user_id o az modele token migrfti bass bud
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
