from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

user = settings.pg_user
password = settings.pg_password
server = settings.pg_host
db = settings.pg_database
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{server}/{db}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
