from typing import List

from fastapi import HTTPException, status, Depends, Response, APIRouter
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
# from app.main import conn, cur
from app.oauth2 import get_current_user_id

# TODO: mituni dependencie authenticate usero inja bzri
router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


# @router.get("/posts/latest")
# async def latest_post():
#     query = "SELECT * FROM posts ORDER BY created_at DESC LIMIT 1"
#     cur.execute(query)
#     last_post = cur.fetchone()
#     return {"latest_post": last_post}
#
#
# @router.get("/posts/{post_id}")
# async def get_post(post_id: int, res: Response):
#     # try:
#     query = "SELECT * FROM posts WHERE id = %s"
#     cur.execute(query, (post_id,))
#     requested_post = cur.fetchone()
#     if not requested_post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {post_id} doesn\'t exist!')
#     return requested_post
#     # except Exception as error:
#     #     print(error)
#     #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
#
#
# @router.get("/posts")
# async def get_all_posts():
#     query = "SELECT * FROM posts"
#     cur.execute(query)
#     all_posts = cur.fetchall()
#     return {"posts": all_posts}
#
#
# @router.post("/posts", status_code=status.HTTP_201_CREATED)
# async def create_post(new_post: schemas.PostCreate):
#     try:
#         query = "INSERT INTO posts(title, content) VALUES(%s, %s) RETURNING *;"
#         cur.execute(query, (new_post.title, new_post.content))
#         inserted_post = cur.fetchone()
#         conn.commit()
#         return {"new_post": inserted_post}
#     except Exception as error:
#         print(error)
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
#
#
# @router.put("/posts/{post_id}")
# async def update_post(post_id: int, updated_post: schemas.PostUpdate):
#     # try:
#     query = "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *"
#     cur.execute(query, (updated_post.title, updated_post.content, updated_post.published, post_id))
#     changed_post = cur.fetchone()
#     if not changed_post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} not found!")
#     conn.commit()
#     return {"updated_post": changed_post}
#     # except Exception as error:
#     #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
#
#
# @router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_post(post_id: int):
#     # try:
#     query = "DELETE FROM posts WHERE id = %s RETURNING id;"
#     cur.execute(query, (post_id,))
#     deleted_post = cur.fetchone()
#     if not deleted_post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} not found!")
#     conn.commit()
#     return Response(status_code=status.HTTP_204_NO_CONTENT)
#     # except Exception as error:
#     #     print(error)
#     #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


@router.get("/", response_model=List[schemas.PostResponse], dependencies=[Depends(get_current_user_id)])
async def all_posts_sqlalchemy(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@router.get("/latest", response_model=schemas.PostResponse, dependencies=[Depends(get_current_user_id)])
async def latest_post(db: Session = Depends(get_db)):
    last_post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()
    return last_post


@router.get("/{post_id}", response_model=schemas.PostResponse, dependencies=[Depends(get_current_user_id)])
async def specific_post_sqlalchemy(post_id, db: Session = Depends(get_db)):
    post = db.query(models.Post).get(post_id)
    # post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} not found!")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_post_sqlalchemy(new_post: schemas.PostCreate, db: Session = Depends(get_db),
                                 user_id: int = Depends(get_current_user_id)):
    try:
        # created_post = models.Post(title=new_post.title, content=new_post.content, published=new_post.published)
        created_post = models.Post(**new_post.dict(), user_id=user_id)
        db.add(created_post)
        db.commit()
        db.refresh(created_post)
        return created_post
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user_id)])
async def delete_post_sqlalchemy(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).get(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} not found!")
    db.delete(post)
    db.commit()


@router.put("/{post_id}", response_model=schemas.PostResponse, dependencies=[Depends(get_current_user_id)])
async def update_post_sqlalchemy(post: schemas.PostUpdate, post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).update(post.dict())
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} not found!")
    db.commit()
    updated_post = db.query(models.Post).get(post_id)
    return updated_post
