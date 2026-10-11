"""
Issue Queue CLI manager:
View, inspect, filter, and resolve unhealable issues logged by LabDoctor.
"""

import sys
import json
from pathlib import Path

# Add workspace root (/Users/jayungerland/gs-os) to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from labdoctor.src.queue.issue_queue import IssueQueue
from labdoctor.src.queue.schema import IssueStatus, FailureCategory


def print_queue_dashboard():
    queue = IssueQueue()
    summary = queue.count_summary()

    print("=" * 65)
    print("📋 LabDoctor Unresolved Issues Queue Dashboard")
    print("=" * 65)
    print(f"Summary by Status: {summary}\n")

    issues = queue.list_issues()
    if not issues:
        print("🎉 No unresolved issues in the queue. All labs are healthy or self-healed!")
        return

    print(f"{'Issue ID':<16} | {'Category':<28} | {'Status':<12} | {'Step Title'}")
    print("-" * 75)
    for issue in issues:
        print(
            f"{issue.issue_id:<16} | {issue.failure_category.value:<28} | {issue.status.value:<12} | {issue.step_title[:25]}"
        )

    print("\n" + "=" * 65)
    print("🔍 Detailed View of Pending / Co-Heal Issues:")
    print("=" * 65)

    for issue in issues:
        if issue.status in (IssueStatus.PENDING, IssueStatus.CO_HEAL_READY):
            print(f"\n📌 [{issue.issue_id}] Lab: {issue.lab_title}")
            print(f"   Step {issue.step_id}: {issue.step_title}")
            print(f"   Category: {issue.failure_category.value}")
            print(f"   Status:   {issue.status.value}")
            print(f"   Diagnosis: {issue.diagnosis}")
            print(f"   Failed Command:\n     $ {issue.failed_command}")
            if issue.candidate_solutions:
                print("   💡 Candidate Solutions identified by Agent:")
                for idx, sol in enumerate(issue.candidate_solutions, 1):
                    print(f"      {idx}. {sol.title}: {sol.description}")
                    if sol.proposed_command:
                        print(f"         Cmd: {sol.proposed_command}")


if __name__ == "__main__":
    print_queue_dashboard()
