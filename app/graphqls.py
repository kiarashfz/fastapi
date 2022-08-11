import strawberry
from strawberry.asgi import GraphQL


@strawberry.input
class UserInp:
    user_id: int
    FName2: str


@strawberry.type
class User:
    id: int
    name: str
    age: int
    fname: str


@strawberry.type
class Query:
    @strawberry.field
    def user(self, user_obj: UserInp) -> User:
        return User(id=user_obj.user_id, name="Patrick", age=100, fname=user_obj.FName2)


schema = strawberry.Schema(query=Query)

graphql_app = GraphQL(schema)

## query
# query ($variable_name: UserInp!){
#     user(userObj: $variable_name){
#         name
#         id
#         fname
#     }
# }

## define variable
# {
#     "variable_name": {
#         "userId": 6,
#         "FName2": "hhh"
#     }
# }
