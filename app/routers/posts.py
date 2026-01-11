from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select, update, func
from typing import List, Optional, Annotated
from sqlalchemy.orm import Session
from .. import schemas, oauth2
from .. import models
from ..database import get_db

router = APIRouter(prefix='/posts', tags=['Posts'])

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, user: Annotated[schemas.UserOut, Depends(oauth2.get_current_active_user)], db: Session = Depends(get_db)):
    post = db.execute(select(models.Post, func.count(models.Vote.post_id).label("likes")).\
        where(models.Post.id == id).\
        join(target=models.Vote, onclause=(models.Vote.post_id == models.Post.id), isouter=True).\
        group_by(models.Post.id)).fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post with that id not found')
    p,l = post
    return {'post': p, 'likes': l}

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(user: Annotated[schemas.UserOut, Depends(oauth2.get_current_active_user)],
              db: Session = Depends(get_db),
              limit: int = 10, skip: int = 0,
              search: Optional[str] = ''): # Get all posts from database
    posts_stmt = select(models.Post, func.count(models.Vote.post_id).label("likes")).\
        join(target=models.Vote, onclause=(models.Vote.post_id == models.Post.id), isouter=True).\
        where(models.Post.title.contains(search)).limit(limit).offset(skip).\
            group_by(models.Post.id)
    res = db.execute(posts_stmt).all()
    return list({"post": post, "likes": likes} for post, likes in res)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate,
                current_user: Annotated[schemas.UserOut, Depends(oauth2.get_current_active_user)], 
                db: Session = Depends(get_db)):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.put("/{id}", response_model=schemas.Post)
def update_posts(updated_post: schemas.PostCreate, id: int, user: Annotated[schemas.UserOut, Depends(oauth2.get_current_active_user)],
                 db: Session = Depends(get_db)):
    post = db.get(models.Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No post associated with that id")
    if post.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    stmt = (
        update(models.Post).
            where(models.Post.owner_id == user.id).
            where(models.Post.id == id).
            values(**updated_post.model_dump())
        )
    db.execute(stmt)
    db.commit()
    db.refresh(post)
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    user: Annotated[schemas.UserOut, Depends(oauth2.get_current_active_user)],
    db: Session = Depends(get_db),
):
    post = db.get(models.Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post associated with that id not found")
    if post.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
