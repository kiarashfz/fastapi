from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
from urllib.parse import quote_plus as urlquote

user = settings.pg_user
password = settings.pg_password
server = settings.pg_host
database = settings.pg_database
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:%s@{server}/{database}" % urlquote(password)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""connect to postgres with psycopg2"""
# import psycopg2
# from psycopg2.extras import RealDictCursor
# from time import sleep

# def connect_to_db(host: str, database: str, user: str, password: str):
#     pg_connection = psycopg2.connect(host=host, database=database, user=user, password=password,
#                                      cursor_factory=RealDictCursor)
#     # Open a cursor to perform database operations
#     pg_cursor = pg_connection.cursor()
#     print('Database connection was successful')
#     return pg_connection, pg_cursor
#
#
# while True:
#     try:
#         conn, cur = connect_to_db(settings.pg_host, settings.pg_database, settings.pg_user, settings.pg_password)
#         break
#     except Exception as err:
#         print('Connecting to database failed!')
#         print(f'Error: {err}')
#         sleep(2)
