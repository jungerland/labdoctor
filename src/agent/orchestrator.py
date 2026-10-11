"""
Orchestrator for LabDoctor:
Executes the parsed lab steps against the GCP Sandbox, detects failures,
triggers diagnosis & healing loops, and packages the result for HITL review.
"""

import uuid
from typing import List, Optional
from pydantic import BaseModel, Field
from labdoctor.src.parser.lab_parser import ParsedLab, LabStep
from labdoctor.src.mcp_tools.gcp_sandbox_server import GCPSandboxTools, CommandResult
from labdoctor.src.queue.issue_queue import IssueQueue
from labdoctor.src.queue.schema import UnresolvedIssue, FailureCategory, IssueStatus, CandidateSolution
from labdoctor.src.playbook.engine import PlaybookEngine
from labdoctor.src.playbook.schema import HealingRule


class StepVerificationResult(BaseModel):
    step_id: int
    step_title: str
    status: str  # "PASSED", "FAILED_FIXED", "FAILED_UNRESOLVED"
    original_command: str
    fixed_command: Optional[str] = None
    root_cause: Optional[str] = None
    fix_rationale: Optional[str] = None
    applied_rule_id: Optional[str] = None
    queued_issue_id: Optional[str] = None
    failure_category: Optional[str] = None
    execution_result: CommandResult
    retry_result: Optional[CommandResult] = None


class LabAuditReport(BaseModel):
    lab_title: str
    total_steps: int
    passed_count: int
    healed_count: int
    failed_count: int
    queued_count: int = 0
    results: List[StepVerificationResult] = Field(default_factory=list)
    estimated_human_hours_saved: float = 0.0


class LabDoctorOrchestrator:
    def __init__(
        self,
        sandbox: Optional[GCPSandboxTools] = None,
        issue_queue: Optional[IssueQueue] = None,
        playbook: Optional[PlaybookEngine] = None,
    ):
        self.sandbox = sandbox or GCPSandboxTools()
        self.issue_queue = issue_queue or IssueQueue()
        self.playbook = playbook or PlaybookEngine()

    def run_audit(self, lab: ParsedLab) -> LabAuditReport:
        results: List[StepVerificationResult] = []
        passed = 0
        healed = 0
        failed = 0

        for step in lab.steps:
            # 1. Execute initial command in sandbox
            res = self.sandbox.execute_bash(step.command)

            if res.exit_code == 0:
                passed += 1
                results.append(
                    StepVerificationResult(
                        step_id=step.step_id,
                        step_title=step.title,
                        status="PASSED",
                        original_command=step.command,
                        execution_result=res,
                    )
                )
            else:
                # 2. Failure detected: Trigger Diagnostic & Self-Healing Loop
                doc_intel = self.sandbox.inspect_gcp_documentation(step.command)
                healed_result = self._heal_step(lab, step, res, doc_intel)

                if healed_result.status == "FAILED_FIXED":
                    healed += 1
                else:
                    failed += 1
                results.append(healed_result)

        queued = sum(1 for r in results if r.queued_issue_id is not None)
        # Estimate ROI: 1.5 human hours saved per self-healed step, 0.5 hours for structured triage
        hours_saved = (passed * 0.1) + (healed * 1.5) + (queued * 0.5)

        return LabAuditReport(
            lab_title=lab.title,
            total_steps=len(lab.steps),
            passed_count=passed,
            healed_count=healed,
            failed_count=failed,
            queued_count=queued,
            results=results,
            estimated_human_hours_saved=round(hours_saved, 2),
        )

    def _heal_step(
        self, lab: ParsedLab, step: LabStep, error_res: CommandResult, doc_intel: str
    ) -> StepVerificationResult:
        """
        Diagnoses failures. If solvable by parameter/syntax fix, auto-heals.
        If it requires architectural decisions or external assets, enqueues to IssueQueue.
        """
        # 1. Consult the Self-Healing Playbook Rules first
        matched_rule = self.playbook.find_matching_rule(step.command, error_res.stderr, error_res.stdout)
        if matched_rule:
            patched_cmd = self.playbook.apply_patch(matched_rule, step.command)
            retry_res = self.sandbox.execute_bash(patched_cmd)
            if retry_res.exit_code == 0:
                return StepVerificationResult(
                    step_id=step.step_id,
                    step_title=step.title,
                    status="FAILED_FIXED",
                    original_command=step.command,
                    fixed_command=patched_cmd,
                    root_cause=matched_rule.name,
                    fix_rationale=matched_rule.description,
                    applied_rule_id=matched_rule.rule_id,
                    execution_result=error_res,
                    retry_result=retry_res,
                )

        # Non-Self-Healable Category A: Missing external dataset / storage asset
        if "BucketNotFoundException" in error_res.stderr or "does not exist" in error_res.stderr:
            issue_id = f"ISSUE-{uuid.uuid4().hex[:8].upper()}"
            issue = UnresolvedIssue(
                issue_id=issue_id,
                lab_path=lab.title,
                lab_title=lab.title,
                step_id=step.step_id,
                step_title=step.title,
                failed_command=step.command,
                error_stdout=error_res.stdout,
                error_stderr=error_res.stderr,
                failure_category=FailureCategory.MISSING_EXTERNAL_ASSET,
                diagnosis=(
                    "The upstream Cloud Storage bucket referenced in this lab no longer exists or permissions were revoked. "
                    "An agent cannot autonomously synthesize or host external customer data assets."
                ),
                candidate_solutions=[
                    CandidateSolution(
                        title="Rehost dataset in official Google Cloud public bucket",
                        description="Move sample_transactions.csv to gs://cloud-training-samples/ and update lab reference.",
                    ),
                    CandidateSolution(
                        title="Generate local synthetic dataset via Python script",
                        description="Inject an inline bash/python command in Step 2 that generates 100 rows of mock CSV data on the fly.",
                        proposed_command="python3 -c \"import pandas as pd; ...\"",
                    ),
                ],
            )
            self.issue_queue.enqueue(issue)
            return StepVerificationResult(
                step_id=step.step_id,
                step_title=step.title,
                status="FAILED_UNRESOLVED",
                original_command=step.command,
                root_cause="External storage bucket is missing (404 Not Found)",
                fix_rationale="Requires curriculum owner decision on where to host replacement dataset.",
                queued_issue_id=issue_id,
                failure_category=FailureCategory.MISSING_EXTERNAL_ASSET.value,
                execution_result=error_res,
            )

        # Non-Self-Healable Category B: Architectural fork / Major generation migration
        if "Cloud Functions 1st gen background triggers are deprecated" in error_res.stderr:
            issue_id = f"ISSUE-{uuid.uuid4().hex[:8].upper()}"
            issue = UnresolvedIssue(
                issue_id=issue_id,
                lab_path=lab.title,
                lab_title=lab.title,
                step_id=step.step_id,
                step_title=step.title,
                failed_command=step.command,
                error_stdout=error_res.stdout,
                error_stderr=error_res.stderr,
                failure_category=FailureCategory.ARCHITECTURAL_CHOICE_NEEDED,
                diagnosis=(
                    "Legacy Cloud Functions 1st gen background triggers are retired. "
                    "Upgrading requires a pedagogical/architectural decision between Cloud Functions 2nd Gen (Eventarc) "
                    "or migrating the lab entirely to Google Cloud Run."
                ),
                candidate_solutions=[
                    CandidateSolution(
                        title="Migrate to Cloud Functions 2nd Gen (Eventarc)",
                        description="Upgrade command to '--gen2' with '--trigger-event-filters=type=google.cloud.storage.object.v1.finalized'.",
                        pros_and_cons="Maintains serverless function paradigm; aligns with Cloud Functions 2.0 exam track.",
                    ),
                    CandidateSolution(
                        title="Refactor lab into Cloud Run Service with Eventarc trigger",
                        description="Wrap code in container and deploy directly to Cloud Run.",
                        pros_and_cons="Provides containerization practice, but increases lab complexity.",
                    ),
                ],
                status=IssueStatus.CO_HEAL_READY,  # Prime for Co-Healing!
            )
            self.issue_queue.enqueue(issue)
            return StepVerificationResult(
                step_id=step.step_id,
                step_title=step.title,
                status="FAILED_UNRESOLVED",
                original_command=step.command,
                root_cause="Architectural deprecation: Cloud Functions v1 triggers obsolete",
                fix_rationale="Multiple viable modern architectures exist; requires human course author architectural decision.",
                queued_issue_id=issue_id,
                failure_category=FailureCategory.ARCHITECTURAL_CHOICE_NEEDED.value,
                execution_result=error_res,
            )

        # Fallback generic failure
        issue_id = f"ISSUE-{uuid.uuid4().hex[:8].upper()}"
        issue = UnresolvedIssue(
            issue_id=issue_id,
            lab_path=lab.title,
            lab_title=lab.title,
            step_id=step.step_id,
            step_title=step.title,
            failed_command=step.command,
            error_stdout=error_res.stdout,
            error_stderr=error_res.stderr,
            failure_category=FailureCategory.UNKNOWN,
            diagnosis=f"Unknown execution error: {error_res.stderr}",
        )
        self.issue_queue.enqueue(issue)
        return StepVerificationResult(
            step_id=step.step_id,
            step_title=step.title,
            status="FAILED_UNRESOLVED",
            original_command=step.command,
            root_cause=f"Execution error with exit code {error_res.exit_code}",
            fix_rationale=error_res.stderr,
            queued_issue_id=issue_id,
            failure_category=FailureCategory.UNKNOWN.value,
            execution_result=error_res,
        )
