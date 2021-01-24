from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import func, desc
from starlette.requests import Request
from pydantic import BaseModel
from db import Score, engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class score_model(BaseModel):
    name: str
    point: int
    difficulty: int


def get_db(request: Request):
    return request.state.db

def get_score(db_session: Session, score_id: int):
    return db_session.query(Score).filter(Score.id == score_id).first()

def get_rank_no(db_session: Session, score_id: int):
    subquery = db_session.query(Score, func.rank().over(order_by=Score.point.desc()).label('rank')).subquery()
    return db_session.query(subquery.c.rank).filter(subquery.c.id == score_id).first()

app = FastAPI(docs_url=None)

@app.get("/api/ranking/all")
async def read_ranking_all(db: Session = Depends(get_db)):
    ranking = db.query(Score).order_by(desc(Score.point)).all()
    count = db.query(Score).count()
    return {"count": count, "ranking": ranking}

@app.get("/api/ranking/top50")
async def read_ranking_top50(db: Session = Depends(get_db)):
    ranking = db.query(Score).order_by(desc(Score.point)).limit(50)
    count = min(50,db.query(Score).count())
    return {"count": count, "ranking": [result for result in ranking]}

@app.post('/api/score')
async def create_score(score_in: score_model, db: Session = Depends(get_db)):
    score = Score(name = score_in.name, point = score_in.point, difficulty = score_in.difficulty)
    db.add(score)
    db.commit()
    score = get_score(db, score.id)
    score.rank = get_rank_no(db, score.id)[0]
    return score

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    request.state.db.close()
    return response