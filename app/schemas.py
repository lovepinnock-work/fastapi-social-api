from typing import Annotated
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
boolint = Annotated[int, Field(strict=True, ge=0, le=1)]

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        from_attributes = True

class PostOut(BaseModel):
    Post: Post
    Likes: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr

class Vote(BaseModel):
    post_id: int
    vote_dir: boolint
    