"""
Generates GitHub Pull Request markdown diffs and summaries
for Human-In-The-Loop review by curriculum instructional designers.
"""

from labdoctor.src.agent.orchestrator import LabAuditReport
from labdoctor.src.parser.lab_parser import ParsedLab


def generate_pr_description(report: LabAuditReport, original_lab: ParsedLab) -> str:
    lines = [
        f"# [LabDoctor Auto-Heal] Fix deprecated GCP commands in: {report.lab_title}",
        "",
        "## Summary of Verification Run",
        f"- **Total Steps Audited**: {report.total_steps}",
        f"- **Direct Passes**: {report.passed_count}",
        f"- **Self-Healed Deprecations**: {report.healed_count}",
        f"- **Unresolved Failures**: {report.failed_count}",
        f"- **Estimated Curriculum Engineering Time Saved**: ~{report.estimated_human_hours_saved} hours",
        "",
        "---",
        "## Detailed Changes & Rationale",
        "",
    ]

    for item in report.results:
        if item.status == "FAILED_FIXED":
            lines.extend(
                [
                    f"### Step {item.step_id}: {item.step_title}",
                    f"**Root Cause**: `{item.root_cause}`",
                    f"**Rationale**: {item.fix_rationale}",
                    "",
                    "```diff",
                    "# Original Command (Failed):",
                ]
            )
            for c_line in item.original_command.splitlines():
                lines.append(f"- {c_line}")

            lines.append("# Fixed Command (Verified in Sandbox):")
            for c_line in item.fixed_command.splitlines():
                lines.append(f"+ {c_line}")

            lines.extend(
                [
                    "```",
                    f"> **Sandbox Output on Retry**: `{item.retry_result.stdout.strip().splitlines()[0]}`",
                    "",
                ]
            )

    lines.extend(
        [
            "## Reviewer Checklist (Human-In-The-Loop)",
            "- [ ] Verify updated commands align with latest Google Cloud certification objectives.",
            "- [ ] Confirm student-facing explanatory text matches the new syntax.",
            "- [ ] Approve & merge.",
        ]
    )

    return "\n".join(lines)


def generate_patched_markdown(original_markdown: str, report: LabAuditReport) -> str:
    """Replaces broken commands with healed commands in the original markdown document."""
    patched = original_markdown
    for item in report.results:
        if item.status == "FAILED_FIXED" and item.fixed_command:
            patched = patched.replace(item.original_command, item.fixed_command)
    return patched
