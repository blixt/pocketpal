import os
from sqlalchemy import create_engine, Column, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import text
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


def run_query_with_session(session, query, **kwargs):
    result = session.execute(text(query), kwargs)
    return result


def run_query(query, **kwargs):
    with Session() as session:
        result = run_query_with_session(session, query, **kwargs)
        session.commit()
        return result


Base = declarative_base()


class Branch(Base):
    __tablename__ = "branches"

    branch_id = Column(String, primary_key=True)
    story_id = Column(
        String, ForeignKey("stories.story_id", ondelete="CASCADE"), index=True
    )
    previous_branch_id = Column(
        String, ForeignKey("branches.branch_id", ondelete="SET NULL"), index=True
    )
    status = Column(String)
    sentiment = Column(String)
    audio_url = Column(String)
    paragraph = Column(Text)
    positive_branch_id = Column(
        String, ForeignKey("branches.branch_id", ondelete="SET NULL")
    )
    negative_branch_id = Column(
        String, ForeignKey("branches.branch_id", ondelete="SET NULL")
    )

    story = relationship("Story", back_populates="branches")
    previous_branch = relationship(
        "Branch", foreign_keys=[previous_branch_id], remote_side=[branch_id]
    )
    positive_branch = relationship(
        "Branch", foreign_keys=[positive_branch_id], remote_side=[branch_id]
    )
    negative_branch = relationship(
        "Branch", foreign_keys=[negative_branch_id], remote_side=[branch_id]
    )

    __table_args__ = (
        CheckConstraint(
            "sentiment IN ('initial_branch', 'positive', 'negative')",
            name="branches_sentiment_check",
        ),
        CheckConstraint(
            "status IN ('generating', 'done', 'failed')", name="branches_status_check"
        ),
    )


class Story(Base):
    __tablename__ = "stories"

    story_id = Column(String, primary_key=True)
    initial_branch_id = Column(
        String, ForeignKey("branches.branch_id", ondelete="SET NULL"), index=True
    )
    title = Column(Text)
    description = Column(Text)
    initial_prompt = Column(Text)

    branches = relationship("Branch", back_populates="story")
    initial_branch = relationship("Branch", foreign_keys=[initial_branch_id])
