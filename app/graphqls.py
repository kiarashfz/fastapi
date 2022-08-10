import strawberry
from strawberry.asgi import GraphQL


@strawberry.input
class UserId:
    user_id: int
    FName2: str


@strawberry.type
class User:
    def __int__(self, user_id):
        self.user_id = user_id

    user_id: int
    name: str
    age: int
    fname: str


@strawberry.type
class Query:
    @strawberry.field
    def user(self, user_id: UserId) -> User:
        return User(user_id=user_id.user_id, name="Patrick", age=100, fname=user_id.FName2)


schema = strawberry.Schema(query=Query)

graphql_app = GraphQL(schema)
