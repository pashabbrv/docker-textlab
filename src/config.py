import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://textlab:textlab_dev_password@localhost:5433/textlab"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = "textlab:jobs:waiting"
PROCESSING_QUEUE = "textlab:jobs:processing"