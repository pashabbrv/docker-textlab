import logging
import signal
import time
from uuid import UUID

from redis import Redis
from redis.exceptions import RedisError

from src.analyzer import analyze
from src.config import PROCESSING_QUEUE, QUEUE_NAME, REDIS_URL
from src.database import SessionLocal, engine
from src.models import AnalysisJob

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("textlab.worker")
stop_requested = False


def handle_signal(signum, frame):
    global stop_requested
    stop_requested = True


def recover_inflight(redis: Redis):
    recovered = 0
    while redis.rpoplpush(PROCESSING_QUEUE, QUEUE_NAME) is not None:
        recovered += 1
    if recovered:
        log.info("Restored %s unfinished job(s)", recovered)


def process(job_id: UUID):
    with SessionLocal() as db:
        job = db.get(AnalysisJob, job_id)
        if job is None or job.status in {"done", "failed"}:
            return
        original_text = job.text
        job.status = "processing"
        db.commit()

    try:
        result = analyze(original_text)
        with SessionLocal() as db:
            job = db.get(AnalysisJob, job_id)
            if job is None:
                return
            job.result = result
            job.status = "done"
            job.error = None
            db.commit()
        log.info("Job %s completed: %s words", job_id, result["words"])
    except Exception as exc:
        log.exception("Job %s failed", job_id)
        with SessionLocal() as db:
            job = db.get(AnalysisJob, job_id)
            if job is not None:
                job.status = "failed"
                job.error = str(exc)[:500]
                db.commit()


def main():
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    redis = Redis.from_url(REDIS_URL, decode_responses=True)
    try:
        recovered = False
        while not stop_requested:
            try:
                if not recovered:
                    recover_inflight(redis)
                    recovered = True
                raw_id = redis.brpoplpush(QUEUE_NAME, PROCESSING_QUEUE, timeout=3)
                if raw_id is None:
                    continue
                try:
                    process(UUID(raw_id))
                except Exception:
                    log.exception("Unexpected failure processing %s", raw_id)
                    continue
                redis.lrem(PROCESSING_QUEUE, 1, raw_id)
            except RedisError:
                recovered = False
                log.warning("Redis is unavailable, retrying", exc_info=True)
                time.sleep(3)
    finally:
        redis.close()
        engine.dispose()
    log.info("Worker stopped")


if __name__ == "__main__":
    main()