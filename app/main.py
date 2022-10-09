from fastapi import FastAPI, Depends

from app import models, websockets
from app.database import engine
from app.graphqls import graphql_app
from app.oauth2 import get_api_key
from app.routers import posts, users, auth, votes
from app.websockets import websocket_endpoint

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    dependencies=[Depends(get_api_key)]
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(votes.router)
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/websocket", websocket_endpoint)
app.include_router(websockets.router)


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
