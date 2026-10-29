from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

JobStatus = Literal["queued", "processing", "done", "failed"]


class JobCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    text: str = Field(min_length=1, max_length=20000, examples=["Привет, Docker! Привет, Python!"])


class WordFrequency(BaseModel):
    word: str
    count: int


class AnalysisResult(BaseModel):
    characters: int
    characters_without_spaces: int
    words: int
    unique_words: int
    sentences: int
    longest_word: str | None
    top_words: list[WordFrequency]


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    status: JobStatus
    result: AnalysisResult | None
    error: str | None
    created_at: datetime
    updated_at: datetime


class StatusCounts(BaseModel):
    queued: int = 0
    processing: int = 0
    done: int = 0
    failed: int = 0