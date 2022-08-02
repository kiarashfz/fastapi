from time import sleep
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session

from .config import settings
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_keys = [
    settings.api_key
]  # This is encrypted in the database


def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if api_key not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )


def connect_to_db(host: str, database: str, user: str, password: str):
    pg_connection = psycopg2.connect(host=host, database=database, user=user, password=password,
                                     cursor_factory=RealDictCursor)
    # Open a cursor to perform database operations
    pg_cursor = pg_connection.cursor()
    print('Database connection was successful')
    return pg_connection, pg_cursor


while True:
    try:
        conn, cur = connect_to_db(settings.pg_host, settings.pg_database, settings.pg_user, settings.pg_password)
        break
    except Exception as err:
        print('Connecting to database failed!')
        print(f'Error: {err}')
        sleep(2)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}", dependencies=[Depends(api_key_auth)])
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/posts/latest")
async def latest_post():
    query = "SELECT * FROM posts ORDER BY created_at DESC LIMIT 1"
    cur.execute(query)
    last_post = cur.fetchone()
    return {"latest_post": last_post}


@app.get("/posts/{post_id}")
async def get_post(post_id: int, res: Response):
    # try:
    query = "SELECT * FROM posts WHERE id = %s"
    cur.execute(query, (post_id,))
    requested_post = cur.fetchone()
    if not requested_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {post_id} doesn\'t exist!')
    return requested_post
    # except Exception as error:
    #     print(error)
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


@app.get("/posts")
async def get_all_posts():
    query = "SELECT * FROM posts"
    cur.execute(query)
    all_posts = cur.fetchall()
    return {"posts": all_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(new_post: Post):
    try:
        query = "INSERT INTO posts(title, content) VALUES(%s, %s) RETURNING *;"
        cur.execute(query, (new_post.title, new_post.content))
        inserted_post = cur.fetchone()
        conn.commit()
        return {"new_post": inserted_post}
    except Exception as error:
        print(error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


@app.put("/posts/{post_id}")
async def update_post(post_id: int, updated_post: Post):
    # try:
    query = "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *"
    cur.execute(query, (updated_post.title, updated_post.content, updated_post.published, post_id))
    changed_post = cur.fetchone()
    if not changed_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} not found!")
    conn.commit()
    return {"updated_post": changed_post}
    # except Exception as error:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int):
    try:
        query = "DELETE FROM posts WHERE id = %s RETURNING id;"
        cur.execute(query, (post_id,))
        deleted_post = cur.fetchone()
        if not deleted_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} not found!")
        conn.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as error:
        print(error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


@app.get("/sqlalchemy/posts")
async def all_posts_sqlalchemy(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"posts": posts}


@app.get("/sqlalchemy/posts/{post_id}")
async def specific_post_sqlalchemy(post_id, db: Session = Depends(get_db)):
    post = db.query(models.Post).get(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} not found!")
    return {"post": post}


@app.post("/sqlalchemy/posts")
async def create_post_sqlalchemy(new_post: Post, db: Session = Depends(get_db)):
    created_post = models.Post(title=new_post.title, content=new_post.content, published=new_post.published)
    db.add(created_post)
    db.commit()
    db.refresh(created_post)
    return {"new_post": created_post}
