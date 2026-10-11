"""
CLI Entrypoint for running the LabDoctor Evaluation Suite.
Displays an engineer-grade Rubric Scorecard with grounded metrics.
"""

import sys
from pathlib import Path

# Add workspace parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
# Add repo root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

try:
    from labdoctor.src.evals.evaluator import LabDoctorEvaluator
except ImportError:
    from src.evals.evaluator import LabDoctorEvaluator


def main():
    console = Console()
    console.print("\n[bold cyan]══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold yellow]🩺 LabDoctor Agentic Evaluation Suite & Grounded Metrics[/bold yellow]")
    console.print("[bold cyan]══════════════════════════════════════════════════════════════[/bold cyan]\n")

    evaluator = LabDoctorEvaluator()
    scorecard = evaluator.run_evaluations()

    # Table of Benchmark Runs
    table = Table(title="Benchmark Execution Matrix", show_header=True, header_style="bold magenta")
    table.add_column("Benchmark ID", style="cyan", width=22)
    table.add_column("Lab Target", style="dim", width=32)
    table.add_column("Result", justify="center", width=10)
    table.add_column("Initial Failures", justify="right", width=16)
    table.add_column("Healed", justify="right", width=10)
    table.add_column("Escalated", justify="right", width=10)

    for bench in scorecard.results:
        status_text = "[bold green]PASS[/bold green]" if bench.passed else "[bold red]FAIL[/bold red]"
        table.add_row(
            bench.benchmark_id,
            bench.lab_file,
            status_text,
            str(bench.initial_failures),
            str(bench.healed_steps),
            str(bench.escalated_issues),
        )

    console.print(table)
    console.print("")

    # Detailed Findings
    for bench in scorecard.results:
        status_bullet = "✅" if bench.passed else "❌"
        console.print(f"{status_bullet} [bold]{bench.benchmark_id}[/bold]:")
        for detail in bench.details:
            console.print(f"   • {detail}")
    console.print("")

    # Scorecard Metrics Panel
    metrics_table = Table(show_header=False, box=None)
    metrics_table.add_column("Metric", style="bold white", width=38)
    metrics_table.add_column("Value", justify="right", style="bold green", width=16)
    metrics_table.add_column("Target Threshold", style="dim", width=20)

    metrics_table.add_row("Fix Pass Rate (FPR)", f"{scorecard.fix_pass_rate_pct}%", ">= 90%")
    metrics_table.add_row("Negative Control Integrity", f"{scorecard.negative_control_integrity_pct}%", "100% (0 False Positives)")
    metrics_table.add_row("Escalation Triage Precision", f"{scorecard.escalation_triage_precision_pct}%", ">= 85%")
    metrics_table.add_row("Pedagogical Preservation Score", f"{scorecard.pedagogical_preservation_score_pct}%", "100% (No Content Drift)")
    metrics_table.add_row("Documentation Grounding Score", f"{scorecard.grounding_score_pct}%", "100% (GCP Docs Grounded)")
    metrics_table.add_row("Total Verified Steps Evaluated", str(scorecard.total_steps_evaluated), "N/A")
    metrics_table.add_row("Est. Human Engineering Hours Saved", f"{scorecard.total_estimated_engineer_hours_saved} hrs", "N/A")
    metrics_table.add_row("Estimated Net Cost Avoidance", f"${scorecard.estimated_cost_avoidance_usd}", "@ $150/hr Staff Eng")

    panel = Panel(
        metrics_table,
        title="[bold green]🏆 Quantitative Verification Scorecard[/bold green]",
        subtitle=f"Overall: {scorecard.passed_benchmarks}/{scorecard.total_benchmarks_evaluated} Benchmarks Passed",
        border_style="green" if scorecard.passed_benchmarks == scorecard.total_benchmarks_evaluated else "red",
    )
    console.print(panel)


if __name__ == "__main__":
    main()
