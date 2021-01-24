from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
import os


SQLALCHEMY_DATABASE_URI = "sqlite:///./test.db"
#SQLALCHEMY_DATABASE_URI = os.environ["SQL_URL"]

engine = create_engine(
    SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}, echo=True
)

Base = declarative_base()

class Score(Base):
    __tablename__ = 'scores'
    id = Column('id', Integer, primary_key = True)
    name = Column('name', String(15))
    point = Column('point', Integer)
    difficulty = Column('difficulty', Integer)
    rank: int = 0

Base.metadata.create_all(bind=engine)