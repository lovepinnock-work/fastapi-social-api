from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select, update, func
from sqlalchemy.orm import Session
from .. import schemas, oauth2
from .. import models
from ..database import get_db, psycopgInit
from typing import List, Optional
import psycopg
from psycopg.rows import dict_row
from typing import Annotated

router = APIRouter(prefix='/posts', tags=['Posts'])

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, user: Annotated[schemas.UserOut, Depends(oauth2.get_current_active_user)], db: Session = Depends(get_db)):
    post = db.execute(select(models.Post, func.count(models.Vote.post_id).label("likes")).\
        join(target=models.Vote, onclause=(models.Vote.post_id == models.Post.id), isouter=True).\
        group_by(models.Post.id)).fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post with that id not found')
    p,l = post
    return {'Post': p, 'Likes': l}

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(user: Annotated[schemas.UserOut, Depends(oauth2.get_current_active_user)],
              db: Session = Depends(get_db),
              limit: int = 10, skip: int = 0,
              search: Optional[str] = ''): # Get all posts from database
    posts = db.scalars(select(models.Post).where(models.Post.title.contains(search))
                       .limit(limit).offset(skip)).all()
    posts1Stmt = select(models.Post, func.count(models.Vote.post_id).label("likes")).\
        join(target=models.Vote, onclause=(models.Vote.post_id == models.Post.id), isouter=True).\
        where(models.Post.title.contains(search)).limit(limit).offset(skip).\
            group_by(models.Post.id)
    # Research Group By, there was a problem not using Vote.post_id vs Post.id
    """
        Resolved:
        1) Required using an execute to get an iterable result object vs scalars
        2) Had to output into dictionary where I controlled the names (Post/Likes)
        3) Had to update schema names to exactly match dictionary names (Post: Post, Likes: int)
        Had to look at how get post worked when it outputs a schema to understand

        When we return in a route from the DB, we return a SQLAlchemy Model or dictionary.
        Our response_model is what we are going to return to the API, its a pydantic model.
        It will look for a corresponding key (case sensitive) within the SQLAlc Model or dict,
        that we define in our schemas (pydantic models). If what is in our schemas doesn't match,
        it will say Field missing. If we send the wrong input from our routes (Expecting dict or 
        object but instead we send None), it will throw a validation error and show you the 
        incorrect input it recieved.
    """
    res = db.execute(posts1Stmt)
    posts1: List = []
    for post, likes in res:
        posts1.append({"Post" : post, "Likes": likes})
    return posts1

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
def delete_post(id: int, user : Annotated[schemas.UserOut, Depends(oauth2.get_current_active_user)]):
    with psycopg.connect(psycopgInit, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            user_deleting = user.id
            post = cur.execute(""" SELECT * FROM posts WHERE id = %s""", (id, )).fetchone()
            if not post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post associated with that id not found")
            if post.get('owner_id', None) != user_deleting:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
            ret = cur.execute("""DELETE FROM posts WHERE id = %s AND owner_id = %s""", (id, user_deleting))
            print(f"Result of executing delete stmt using execute: {ret.fetchall()}")
            return Response(status_code=status.HTTP_204_NO_CONTENT)