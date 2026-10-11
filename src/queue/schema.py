"""
Schemas for Unresolved LabDoctor Issues and Failure Classifications.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class FailureCategory(str, Enum):
    ARCHITECTURAL_CHOICE_NEEDED = "ARCHITECTURAL_CHOICE_NEEDED"
    MISSING_EXTERNAL_ASSET = "MISSING_EXTERNAL_ASSET"
    QUOTA_OR_ORG_POLICY = "QUOTA_OR_ORG_POLICY"
    SECURITY_OR_PERM_RISK = "SECURITY_OR_PERM_RISK"
    UPSTREAM_API_BREAK = "UPSTREAM_API_BREAK"
    UNKNOWN = "UNKNOWN"


class IssueStatus(str, Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    CO_HEAL_READY = "CO_HEAL_READY"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class CandidateSolution(BaseModel):
    title: str
    description: str
    proposed_command: Optional[str] = None
    pros_and_cons: Optional[str] = None


class UnresolvedIssue(BaseModel):
    issue_id: str
    lab_path: str
    lab_title: str
    step_id: int
    step_title: str
    failed_command: str
    error_stdout: str
    error_stderr: str
    failure_category: FailureCategory
    diagnosis: str
    candidate_solutions: List[CandidateSolution] = Field(default_factory=list)
    status: IssueStatus = IssueStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    applied_command: Optional[str] = None
    learned_rule_id: Optional[str] = None
