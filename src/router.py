from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from src import repository
from src.config import QUEUE_NAME
from src.database import get_db
from src.schemas import JobCreate, JobRead, StatusCounts

router = APIRouter(tags=["Text analysis jobs"])


@router.post("/jobs", response_model=JobRead, status_code=status.HTTP_202_ACCEPTED)
def create_job(payload: JobCreate, request: Request, db: Session = Depends(get_db)):
    job = repository.create_job(db, payload.text)
    try:
        request.app.state.redis.lpush(QUEUE_NAME, str(job.id))
    except RedisError as exc:
        job.status = "failed"
        job.error = "Не удалось поставить задачу в очередь Redis"
        db.commit()
        raise HTTPException(status_code=503, detail="Очередь Redis недоступна") from exc
    return job


@router.get("/jobs", response_model=list[JobRead])
def list_jobs(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return repository.list_jobs(db, limit)


@router.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: UUID, db: Session = Depends(get_db)):
    job = repository.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return job


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: UUID, db: Session = Depends(get_db)):
    job = repository.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    db.delete(job)
    db.commit()


@router.get("/stats", response_model=StatusCounts, tags=["Statistics"])
def stats(db: Session = Depends(get_db)):
    return repository.get_status_counts(db)