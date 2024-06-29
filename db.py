import os

import sqlalchemy
from google.cloud.sql.connector import Connector

# See Notion for environment variables
DB_PASS = os.environ.get("DB_PASS")
DB_USER = os.environ.get("DB_USER")
DB_NAME = os.environ.get("DB_NAME")
INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")


def run_query(query: str):
    """Get query results"""

    connector = Connector()

    def getconn():
        connection = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME
        )
        return connection

    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )

    with pool.connect() as db_conn:
        results = db_conn.execute(
            sqlalchemy.text(query)
        ).fetchall()

    connector.close()

    return results
