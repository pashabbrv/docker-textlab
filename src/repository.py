from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models import AnalysisJob


def create_job(db: Session, text: str) -> AnalysisJob:
    job = AnalysisJob(text=text, status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: UUID) -> AnalysisJob | None:
    return db.get(AnalysisJob, job_id)


def list_jobs(db: Session, limit: int) -> list[AnalysisJob]:
    return list(db.scalars(select(AnalysisJob).order_by(AnalysisJob.created_at.desc()).limit(limit)))


def get_status_counts(db: Session) -> dict[str, int]:
    counters = {"queued": 0, "processing": 0, "done": 0, "failed": 0}
    rows = db.execute(select(AnalysisJob.status, func.count()).group_by(AnalysisJob.status))
    for status, count in rows:
        if status in counters:
            counters[status] = count
    return counters