from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import utils
from ..schemas import UserCreate, UserOut
from ..database import get_db
from ..models import User

router = APIRouter(prefix='/users', tags=['Users'])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)
    created_user = User(**user.model_dump())
    db.add(created_user)
    db.commit()
    db.refresh(created_user)
    return created_user

@router.get("/{id}", response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with that id found!")
    return user
