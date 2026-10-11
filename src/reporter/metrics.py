"""
BigQuery Telemetry and ROI modeling module.
Tracks lab reliability, breakage frequency, API drift, and operational ROI.
"""

from datetime import datetime, timezone
from typing import Dict, Any
from labdoctor.src.agent.orchestrator import LabAuditReport


def export_bigquery_record(report: LabAuditReport, lab_path: str) -> Dict[str, Any]:
    """
    Formats the audit results into a structured BigQuery row
    ready for operational dashboards (e.g. Looker Studio).
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lab_path": lab_path,
        "lab_title": report.lab_title,
        "total_steps": report.total_steps,
        "passed_steps": report.passed_count,
        "healed_steps": report.healed_count,
        "failed_steps": report.failed_count,
        "reliability_score": (
            (report.passed_count + report.healed_count) / report.total_steps
            if report.total_steps > 0
            else 0.0
        ),
        "engineering_hours_saved": report.estimated_human_hours_saved,
        "drift_breakdown": [
            {
                "step_id": r.step_id,
                "step_title": r.step_title,
                "status": r.status,
                "root_cause": r.root_cause,
            }
            for r in report.results
            if r.status != "PASSED"
        ],
    }
