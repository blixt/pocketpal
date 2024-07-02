import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.orm import Session as SQLAlchemySession
from google.cloud.sql.connector import Connector


# Database configuration
# See Notion for environment variables
DB_PASS = os.environ.get("DB_PASS")
DB_USER = os.environ.get("DB_USER")
DB_NAME = os.environ.get("DB_NAME")
INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")

# Connection pooling setup
connector = Connector()


def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME, "pg8000", user=DB_USER, password=DB_PASS, db=DB_NAME
    )
    return conn


engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

Session = sessionmaker(bind=engine)


def run_query_with_session(session: SQLAlchemySession, query: str, **kwargs):
    result = session.execute(text(query), kwargs)
    return result


def run_query(query: str, **kwargs):
    with Session() as session:
        result = run_query_with_session(session, query, **kwargs)
        session.commit()
        return result
