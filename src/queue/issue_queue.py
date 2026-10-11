"""
Persistent Issue Queue Store for LabDoctor.
Manages unresolved lab failures, supports filtering, claiming, and updating.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from labdoctor.src.queue.schema import UnresolvedIssue, IssueStatus, FailureCategory


class IssueQueue:
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = (
                Path(__file__).resolve().parent.parent.parent / "data" / "unresolved_issues.json"
            )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage()

    def _ensure_storage(self):
        if not self.storage_path.exists():
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def _load_all(self) -> List[UnresolvedIssue]:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [UnresolvedIssue(**item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_all(self, issues: List[UnresolvedIssue]):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([issue.model_dump() for issue in issues], f, indent=2)

    def enqueue(self, issue: UnresolvedIssue) -> UnresolvedIssue:
        issues = self._load_all()
        # Avoid exact duplicate active issues for the same step in the same lab
        existing = next(
            (
                i for i in issues
                if i.lab_path == issue.lab_path
                and i.step_id == issue.step_id
                and i.status in (IssueStatus.PENDING, IssueStatus.IN_REVIEW, IssueStatus.CO_HEAL_READY)
            ),
            None,
        )
        if existing:
            return existing

        issues.append(issue)
        self._save_all(issues)
        return issue

    def list_issues(
        self,
        status: Optional[IssueStatus] = None,
        category: Optional[FailureCategory] = None,
    ) -> List[UnresolvedIssue]:
        issues = self._load_all()
        if status:
            issues = [i for i in issues if i.status == status]
        if category:
            issues = [i for i in issues if i.failure_category == category]
        return issues

    def get_issue(self, issue_id: str) -> Optional[UnresolvedIssue]:
        issues = self._load_all()
        return next((i for i in issues if i.issue_id == issue_id), None)

    def update_status(
        self,
        issue_id: str,
        status: IssueStatus,
        resolved_by: Optional[str] = None,
        resolution_notes: Optional[str] = None,
        applied_command: Optional[str] = None,
    ) -> Optional[UnresolvedIssue]:
        issues = self._load_all()
        target = None
        for i in issues:
            if i.issue_id == issue_id:
                i.status = status
                if resolved_by:
                    i.resolved_by = resolved_by
                if resolution_notes:
                    i.resolution_notes = resolution_notes
                if applied_command:
                    i.applied_command = applied_command
                target = i
                break
        if target:
            self._save_all(issues)
        return target

    def count_summary(self) -> Dict[str, int]:
        issues = self._load_all()
        summary = {s.value: 0 for s in IssueStatus}
        for i in issues:
            summary[i.status.value] = summary.get(i.status.value, 0) + 1
        return summary
