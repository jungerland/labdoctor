"""
Playbook Learner CLI:
Allows resolving an issue from the queue and automatically compiling
the resolution into a new persistent Self-Healing Playbook rule.
"""

import sys
import uuid
from pathlib import Path

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from labdoctor.src.queue.issue_queue import IssueQueue
from labdoctor.src.queue.schema import IssueStatus
from labdoctor.src.playbook.engine import PlaybookEngine
from labdoctor.src.playbook.schema import HealingRule, PatchStrategy, MatchCondition


def learn_from_issue(
    issue_id: str,
    rule_name: str,
    strategy: PatchStrategy,
    find_target: str,
    replace_with: str,
    engineer_name: str = "curriculum-lead",
):
    queue = IssueQueue()
    playbook = PlaybookEngine()

    issue = queue.get_issue(issue_id)
    if not issue:
        print(f"❌ Error: Issue {issue_id} not found in queue.")
        return

    rule_id = f"RULE-{uuid.uuid4().hex[:6].upper()}"

    # Construct the newly learned rule
    new_rule = HealingRule(
        rule_id=rule_id,
        name=rule_name,
        description=f"Auto-learned from {issue_id}: {issue.diagnosis[:80]}...",
        category=issue.failure_category.value,
        error_pattern=issue.error_stderr[:60].strip(),
        command_pattern=issue.failed_command.split()[0] if issue.failed_command else None,
        match_condition=MatchCondition.CONTAINS_ERROR,
        strategy=strategy,
        find_target=find_target,
        replace_with=replace_with,
        learned_from_issue_id=issue_id,
        author=engineer_name,
    )

    # Register in playbook
    playbook.register_rule(new_rule)
    print(f"✅ Successfully created and registered Playbook Rule: [{rule_id}] {rule_name}")

    # Mark issue as resolved in queue
    queue.update_status(
        issue_id=issue_id,
        status=IssueStatus.RESOLVED,
        resolved_by=engineer_name,
        resolution_notes=f"Converted into autonomous Playbook Rule {rule_id}.",
    )
    print(f"✅ Issue {issue_id} marked as RESOLVED in queue.")


def list_playbook_rules():
    playbook = PlaybookEngine()
    rules = playbook.load_rules()
    print("=" * 65)
    print("📖 LabDoctor Self-Healing Playbook Rules")
    print("=" * 65)
    for r in rules:
        print(f"[{r.rule_id}] {r.name} ({r.category})")
        print(f"   Match:   '{r.error_pattern}'")
        print(f"   Action:  Strategy={r.strategy.value} | Find='{r.find_target}' -> Replace='{r.replace_with}'")
        print(f"   Applied: {r.times_applied} times | Author: {r.author}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_playbook_rules()
    else:
        # Example interactive invocation demonstration:
        # Resolve the missing bucket issue by teaching LabDoctor to redirect to official public bucket
        queue = IssueQueue()
        pending = queue.list_issues(status=IssueStatus.PENDING)
        if pending:
            target_issue = pending[0]
            print(f"Teaching LabDoctor how to heal {target_issue.issue_id}...")
            learn_from_issue(
                issue_id=target_issue.issue_id,
                rule_name="Redirect Legacy Sample Bucket to Official Public Bucket",
                strategy=PatchStrategy.REPLACE_FLAG,
                find_target="gs://expired-legacy-training-bucket-2022/",
                replace_with="gs://cloud-training-samples-official/",
                engineer_name="Google Learning Specialist",
            )
        else:
            list_playbook_rules()
