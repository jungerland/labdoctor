"""
LabDoctor CLI entrypoint:
Demonstrates the full agentic verification, self-healing, and PR generation pipeline.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from labdoctor.src.parser.lab_parser import parse_markdown_lab
from labdoctor.src.agent.orchestrator import LabDoctorOrchestrator
from labdoctor.src.reporter.pr_generator import (
    generate_pr_description,
    generate_patched_markdown,
)
from labdoctor.src.reporter.metrics import export_bigquery_record


def main():
    target_arg = sys.argv[1] if len(sys.argv) > 1 else "complex"
    filename = "complex_broken_lab.md" if target_arg == "complex" else "broken_cloud_run_lab.md"
    sample_lab_path = (
        Path(__file__).resolve().parent / "sample_labs" / filename
    )

    print(f"==================================================")
    print(f"🩺 LabDoctor: Autonomous GCP Lab Verification Agent")
    print(f"==================================================")
    print(f"[+] Loading lab: {sample_lab_path.name}")

    with open(sample_lab_path, "r", encoding="utf-8") as f:
        raw_markdown = f.read()

    # Step 1: Parse markdown
    parsed_lab = parse_markdown_lab(raw_markdown)
    print(f"[+] Extracted {len(parsed_lab.steps)} actionable steps:")
    for step in parsed_lab.steps:
        print(f"    - Step {step.step_id}: {step.title}")

    # Step 2: Run verification and self-healing loop
    print("\n[+] Running agent verification against GCP Sandbox (MCP Tools)...")
    orchestrator = LabDoctorOrchestrator()
    audit_report = orchestrator.run_audit(parsed_lab)

    print("\n[+] Verification Results:")
    print(f"    - Direct Passes:  {audit_report.passed_count}")
    print(f"    - Self-Healed:    {audit_report.healed_count}")
    print(f"    - Unresolved:     {audit_report.failed_count}")
    print(f"    - Est. Hours Saved: ~{audit_report.estimated_human_hours_saved} hrs")

    # Step 3: Generate Pull Request for HITL
    print("\n[+] Generating GitHub Pull Request & Diff...")
    pr_desc = generate_pr_description(audit_report, parsed_lab)
    print("\n" + ("=" * 50))
    print(pr_desc)
    print("=" * 50)

    # Step 4: BigQuery Telemetry Output
    bq_record = export_bigquery_record(audit_report, str(sample_lab_path))
    print("\n[+] BigQuery Operational Telemetry Event:")
    print(json.dumps(bq_record, indent=2))

    # Step 5: Save Patched Markdown
    patched_md = generate_patched_markdown(raw_markdown, audit_report)
    out_path = sample_lab_path.parent / "healed_cloud_run_lab.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(patched_md)
    print(f"\n[+] Successfully saved healed lab to: {out_path.name}")


if __name__ == "__main__":
    main()
