from .. import utils
from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas import UserCreate, UserOut
from ..database import get_db
from ..models import User
from sqlalchemy.orm import Session

router = APIRouter(prefix='/users', tags=['Users'])

@router.post("/", response_model=UserOut)
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
# Step 2: User account creation path operation called user
# Step 8: Import utils
# Step 9: Set up route to fetch data on user based on id called get users , path=users/id, test
# Step 10: Routers