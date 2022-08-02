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
