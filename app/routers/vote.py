from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, delete
from ..database import get_db, Session
from ..oauth2 import get_current_active_user
from .. import models, schemas

router = APIRouter(prefix='/vote', tags=['Vote'])

@router.post("/", status_code=status.HTTP_201_CREATED)
def cast_vote(casted_vote: schemas.Vote, 
              curr_user : Annotated[schemas.UserOut, Depends(get_current_active_user)],
              db: Session = Depends(get_db)):
    if curr_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Must be signed in to cast vote")
    postExists = db.get(models.Post, casted_vote.post_id)
    if not postExists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post with that id does not exist")
    foundVote = db.scalar(select(models.Vote).where(models.Vote.post_id == casted_vote.post_id)
                .where(models.Vote.user_id == curr_user.id))    
    if casted_vote.vote_dir == 1: # User is adding a vote
        # Ensure no duplicate vote
        if foundVote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User w/ id {curr_user.id} has already liked this post")
        # Insert user vote
        db.execute(insert(models.Vote).values(post_id=casted_vote.post_id, user_id=curr_user.id))
        db.commit() 
        return {"message": "Successfully added vote"}
    else:
        #Ensure vote exists
        if not foundVote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has not liked this post")
        #Delete vote
        db.execute(delete(models.Vote).where(models.Vote.post_id == casted_vote.post_id).
                where(models.Vote.user_id == curr_user.id))
        db.commit()
        return {"message": "Vote successfully removed"}