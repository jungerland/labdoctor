"""
Evaluation Rubric Schema and Metrics Model for LabDoctor.
Encapsulates quantitative metrics: Fix Pass Rate (FPR), False Positive Rate,
Grounding Score, Escalation Precision, and Pedagogical Preservation.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LabBenchmarkExpectation(BaseModel):
    benchmark_id: str
    lab_file: str
    description: str
    expected_initial_failures: int
    expected_healed_steps: int
    expected_escalated_issues: int
    expected_failure_categories: List[str] = Field(default_factory=list)
    is_negative_control: bool = False  # Should pass with 0 edits


class LabBenchmarkEvaluation(BaseModel):
    benchmark_id: str
    lab_file: str
    passed: bool
    initial_failures: int
    healed_steps: int
    escalated_issues: int
    false_positives: int = 0
    hallucinated_modifications: int = 0
    pedagogical_drift_detected: bool = False
    details: List[str] = Field(default_factory=list)


class EvaluationScorecard(BaseModel):
    total_benchmarks_evaluated: int
    passed_benchmarks: int
    
    # Core Metrics
    total_steps_evaluated: int
    fix_pass_rate_pct: float  # (successful heals / total healable failures) * 100
    negative_control_integrity_pct: float  # (clean labs left untouched / total clean labs) * 100
    escalation_triage_precision_pct: float  # (correctly categorized escalations / total escalations) * 100
    pedagogical_preservation_score_pct: float  # (labs without pedagogical drift / total labs) * 100
    grounding_score_pct: float  # (heals grounded in doc lookups or verified rules / total heals) * 100
    
    # Financial / Operational ROI
    total_estimated_engineer_hours_saved: float
    estimated_cost_avoidance_usd: float  # Based on $150/hr Google Cloud Staff Curriculum Eng
    
    results: List[LabBenchmarkEvaluation] = Field(default_factory=list)
