import os

# pip install "cloud-sql-python-connector[pg8000]" 
from google.cloud.sql.connector import Connector
import sqlalchemy

# See Notion for environment variables
DB_PASS = os.environ.get("DB_PASS")
DB_USER = os.environ.get("DB_USER")
DB_NAME = os.environ.get("DB_NAME")
INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")

connector = Connector()

def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn

pool = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

with pool.connect() as db_conn:
    results = db_conn.execute(sqlalchemy.text("SELECT * FROM ratings")).fetchall()

    for row in results:
        print(row)

connector.close()