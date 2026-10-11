"""
Automated unit tests for LabDoctor evaluation suite.
Ensures metrics calculation, negative controls, and benchmark harnesses behave reliably.
"""

import pytest
from src.evals.evaluator import LabDoctorEvaluator


def test_evaluator_benchmark_execution():
    evaluator = LabDoctorEvaluator()
    scorecard = evaluator.run_evaluations()

    assert scorecard.total_benchmarks_evaluated == 4
    assert scorecard.passed_benchmarks == 4
    assert scorecard.fix_pass_rate_pct == 100.0
    assert scorecard.negative_control_integrity_pct == 100.0
    assert scorecard.escalation_triage_precision_pct == 100.0
    assert scorecard.pedagogical_preservation_score_pct == 100.0
    assert scorecard.grounding_score_pct == 100.0
    assert scorecard.total_steps_evaluated == 12
    assert scorecard.total_estimated_engineer_hours_saved > 0.0
