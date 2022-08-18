import datetime

from pydantic import BaseModel, Extra, EmailStr, conint


class UserBase(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str
    created_at: datetime.datetime


class UserLogin(UserBase):
    password: str


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

    class Config:
        orm_mode = True
        extra = Extra.forbid


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime.datetime
    user_id: int
    user: UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True


class LoginResponse(UserBase, Token):
    pass


class TokenData(BaseModel):
    email: EmailStr


class TokenDataUserId(BaseModel):
    user_id: int


class VoteBase(BaseModel):
    post_id: int

    class Config:
        orm_mode = True


class VoteCreate(VoteBase):
    dir: conint(le=1, ge=0)


class VoteResponse(VoteBase):
    user_id: int
    user: UserResponse
