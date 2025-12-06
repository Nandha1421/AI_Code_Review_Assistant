from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Issue(BaseModel):
    id: str
    rule: Optional[str]
    message: str
    severity: Severity
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    suggested_fix: Optional[str] = None
    explanation: Optional[str] = None


class ReviewRequest(BaseModel):
    code: str
    language: str = "python"
    filename: Optional[str] = None


class ReviewResponse(BaseModel):
    issues: List[Issue]
    summary: Optional[str] = None
    