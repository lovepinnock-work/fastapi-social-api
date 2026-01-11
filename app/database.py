import psycopg
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .config import settings

#Generic schema for DB_URL = dialect(mysql/postgres)+driver(psycopg)://username:password@host:port/database

SQLALCHEMY_DATABASE_URL = f"{settings.database_dialect}+{settings.database_driver}://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       pool_size=10,
                       max_overflow=20,
                       pool_timeout=30,
                       pool_pre_ping=True)

def get_db():
    with Session(bind=engine, autocommit=False, autoflush=False) as session:
        yield session

psycopgInit = f"dbname={settings.database_name} user={settings.database_username} password={settings.database_password} host={settings.database_hostname}"
try:
    with psycopg.connect(psycopgInit) as conn:
        print("Connection successfully established")
except Exception as error:
    print("Error: ", error)