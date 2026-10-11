"""
Playbook Engine for LabDoctor:
Loads healing rules, evaluates errors against rules, applies patches,
and records newly learned recipes from issue resolutions.
"""

import json
import re
from pathlib import Path
from typing import List, Optional, Tuple
from labdoctor.src.playbook.schema import HealingRule, PatchStrategy, MatchCondition


class PlaybookEngine:
    def __init__(self, rules_path: Optional[str] = None):
        if rules_path:
            self.rules_path = Path(rules_path)
        else:
            self.rules_path = Path(__file__).resolve().parent / "rules.json"
        self._ensure_file()

    def _ensure_file(self):
        if not self.rules_path.exists():
            with open(self.rules_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def load_rules(self) -> List[HealingRule]:
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [HealingRule(**item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_rules(self, rules: List[HealingRule]):
        with open(self.rules_path, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in rules], f, indent=2)

    def register_rule(self, rule: HealingRule) -> HealingRule:
        """Adds a newly learned healing rule to the playbook."""
        rules = self.load_rules()
        existing = next((r for r in rules if r.rule_id == rule.rule_id), None)
        if existing:
            return existing
        rules.append(rule)
        self.save_rules(rules)
        return rule

    def find_matching_rule(self, command: str, stderr: str, stdout: str) -> Optional[HealingRule]:
        """Scans all rules in the playbook to find one that matches the error pattern."""
        rules = self.load_rules()
        for rule in rules:
            # Check command pattern filter if specified
            if rule.command_pattern and rule.command_pattern not in command:
                continue

            # Check error pattern match
            if rule.match_condition == MatchCondition.CONTAINS_ERROR:
                if rule.error_pattern in stderr or rule.error_pattern in stdout:
                    return rule
            elif rule.match_condition == MatchCondition.REGEX_ERROR:
                if re.search(rule.error_pattern, stderr) or re.search(rule.error_pattern, stdout):
                    return rule
            elif rule.match_condition == MatchCondition.CONTAINS_COMMAND:
                if rule.error_pattern in command:
                    return rule

        return None

    def apply_patch(self, rule: HealingRule, original_command: str) -> str:
        """Applies the rule's patch strategy to heal the command."""
        patched = original_command

        if rule.strategy == PatchStrategy.REMOVE_FLAG:
            if rule.find_target:
                # Remove flag with trailing backslashes/whitespace
                pattern = rf"{re.escape(rule.find_target)}\s*(\\?\n\s*)?"
                patched = re.sub(pattern, "", original_command)

        elif rule.strategy == PatchStrategy.REPLACE_FLAG:
            if rule.find_target and rule.replace_with is not None:
                patched = original_command.replace(rule.find_target, rule.replace_with)

        elif rule.strategy == PatchStrategy.REPLACE_COMMAND:
            if rule.replacement_template:
                patched = rule.replacement_template

        # Increment rule usage telemetry
        self._record_rule_application(rule.rule_id)
        return patched.strip()

    def _record_rule_application(self, rule_id: str):
        rules = self.load_rules()
        for r in rules:
            if r.rule_id == rule_id:
                r.times_applied += 1
                break
        self.save_rules(rules)
