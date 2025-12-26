import time
import psycopg
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .config import settings

#Generic schema for DB_URL = dialect(mysql/postgres)+driver(psycopg)://username:password@host:port/database

SQLALCHEMY_DATABASE_URL = f"{settings.database_dialect}+{settings.database_driver}://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def get_db():
    with Session(bind=engine, autocommit=False, autoflush=False) as session:
        yield session

psycopgInit = f"dbname={settings.database_name} user={settings.database_username} password={settings.database_password} host={settings.database_hostname}"
try:
    with psycopg.connect(psycopgInit) as conn:
        # Open a cursor to perform database operations
        print("Connection successfully established")
except Exception as error:
    print("Error: ", error)

"""   try:
        with psycopg.connect(psycopgInit, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                                SELECT *
                                FROM posts
                                WHERE id = %s
                            , (id,))
                post = cur.fetchone()
                if not post: # No Post with that id was found
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Post Found Associated With That Id")
                return {"post" : post}
    except HTTPException as hError:
        print("ID Error: ", hError)
    except Exception as error:
        print("Error: ", error)
"""