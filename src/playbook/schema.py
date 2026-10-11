"""
Schema and rule models for LabDoctor's Self-Healing Playbook.
Allows learning new healing recipes from human resolutions or verified repairs.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class MatchCondition(str, Enum):
    CONTAINS_ERROR = "CONTAINS_ERROR"
    REGEX_ERROR = "REGEX_ERROR"
    CONTAINS_COMMAND = "CONTAINS_COMMAND"
    EXIT_CODE = "EXIT_CODE"


class PatchStrategy(str, Enum):
    REPLACE_FLAG = "REPLACE_FLAG"
    REMOVE_FLAG = "REMOVE_FLAG"
    REPLACE_COMMAND = "REPLACE_COMMAND"
    INJECT_PRE_STEP = "INJECT_PRE_STEP"
    CUSTOM_TRANSFORM = "CUSTOM_TRANSFORM"


class HealingRule(BaseModel):
    rule_id: str
    name: str
    description: str
    category: str
    # Matching criteria
    error_pattern: str
    command_pattern: Optional[str] = None
    match_condition: MatchCondition = MatchCondition.CONTAINS_ERROR
    # Healing action
    strategy: PatchStrategy
    find_target: Optional[str] = None
    replace_with: Optional[str] = None
    replacement_template: Optional[str] = None
    # Provenance & Metadata
    learned_from_issue_id: Optional[str] = None
    author: str = "curriculum-engineer"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    times_applied: int = 0
    success_rate: float = 1.0
