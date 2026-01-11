from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(prefix='/health', tags=["Health"])

@router.get('/', status_code=status.HTTP_200_OK)
def health(db: Session = Depends(get_db)):
    retVal = db.execute(text("SELECT 1")).scalar()
    if retVal is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return {"App Status" : "Running", "DB Status": "Running"}