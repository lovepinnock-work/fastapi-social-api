from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, Field

#Define our own datatype using Annotated and Field
boolint = Annotated[int, Field(strict=True, ge=0, le=1)]

# User models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    model_config = ConfigDict(from_attributes=True)

class UserOut(BaseModel):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Post models
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
    model_config = ConfigDict(from_attributes=True)

class PostOut(BaseModel):
    post: Post
    likes: int       
    model_config = ConfigDict(from_attributes=True)

# Token Models
class Token(BaseModel):
    token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr

# Vote Model
class Vote(BaseModel):
    post_id: int
    vote_dir: boolint
    