from time import sleep

import psycopg2
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from psycopg2.extras import RealDictCursor

from app import models
from app.config import settings
from app.database import engine
from app.routers import posts, users, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# api_keys = [
#     settings.api_key
# ]  # This is encrypted in the database

#
# def api_key_auth(api_key: str = Depends(oauth2_scheme)):
#     if api_key not in api_keys:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Forbidden"
#         )


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


@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.get("/items/")
# async def read_items(token: str = Depends(oauth2_scheme)):
#     return {"token": token}


# @app.get("/hello/{name}", dependencies=[Depends(api_key_auth)])
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
