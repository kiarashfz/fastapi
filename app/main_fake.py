from time import sleep

from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor


def connect_to_db():
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Te567jex97?!@eRd',
                            cursor_factory=RealDictCursor)
    # Open a cursor to perform database operations
    cur = conn.cursor()
    print('Database connection was successful')
    return conn, cur


while True:
    try:
        conn, cur = connect_to_db()
        break
    except Exception as err:
        print('Connecting to database failed!')
        print(f'Error: {err}')
        sleep(2)

# while True:
#     try:
#         # Connect to your postgres DB
#         conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Te567jex97?!@eRd',
#                                 cursor_factory=RealDictCursor)
#         # Open a cursor to perform database operations
#         cur = conn.cursor()
#         print('Database connection was successful')
#         break
#     except Exception as err:
#         print('Connecting to database failed!')
#         print(f'Error: {err}')
#         sleep(2)


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # use token authentication
api_keys = [
    "akljnv13bvi2vfo0b0bw"
]  # This is encrypted in the database


def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if api_key not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )


class Post(BaseModel):
    # id: int
    title: str
    content: str
    published: bool = True
    # rating: Optional[int]


posts = [
    {"id": 1, "title": "t1", "content": "c1"},
    {"id": 2, "title": "t2", "content": "c2"},
    {"id": 3, "title": "t3", "content": "c3"},
    {"id": 4, "title": "t4", "content": "c4"},
]


def find_post_by_id(post_id: int):
    return list(filter(lambda post: post["id"] == post_id, posts))[0]


def remove_post(post_id: int):
    post = find_post_by_id(post_id)
    posts.remove(post)


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


# @app.get("/posts/{post_id}")
# async def get_post(post_id: int, res: Response):
#     try:
#         requested_post = find_post_by_id(post_id)
#         return {f"post {post_id}": requested_post}
#     except IndexError as err:
#         res.status_code = status.HTTP_404_NOT_FOUND
#         return err.__str__()

@app.get("/posts/{post_id}")
async def get_post(post_id: int, res: Response):
    try:
        query = "SELECT * FROM posts WHERE id = %s"
        cur.execute(query, (post_id,))
        requested_post = cur.fetchone()
        if not requested_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {post_id} doesn\'t exist!')
        return requested_post
    except Exception as error:
        print(error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


# try:
#     requested_post = find_post_by_id(post_id)
#     return {f"post {post_id}": requested_post}

# except IndexError as error:
#     print(error)
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {post_id} doesn\'t exist!')


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

    # posts.append(new_post.dict())
    # return {
    #     "new_post": f'{new_post.title}: {new_post.content} | published: {new_post.published} | rating: {new_post.rating}'
    # }


@app.put("/posts/{post_id}")
async def update_post(post_id: int, updated_post: Post):
    try:
        query = "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *"
        cur.execute(query, (updated_post.title, updated_post.content, updated_post.published, post_id))
        changed_post = cur.fetchone()
        if not changed_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} not found!")
        conn.commit()
        return {"updated_post": changed_post}
    except Exception as error:
        print(error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
    # try:
    #     specific_post = find_post_by_id(int(post_id))
    # except IndexError as err:
    #     print(err)
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} not found!")
    # ind = posts.index(specific_post)
    # posts[ind] = updated_post.dict()
    # return posts[ind]


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

    # try:
    #     remove_post(post_id)
    #     return Response(status_code=status.HTTP_204_NO_CONTENT)
    # except IndexError:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {post_id} not found!")
