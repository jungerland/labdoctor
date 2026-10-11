import re
from typing import List, Optional
from pydantic import BaseModel, Field


class LabStep(BaseModel):
    step_id: int
    title: str
    description: str
    command_type: str = "bash"  # bash, terraform, python
    command: str
    expected_output: Optional[str] = None
    raw_markdown_chunk: str


class ParsedLab(BaseModel):
    title: str
    overview: str
    steps: List[LabStep] = Field(default_factory=list)


def parse_markdown_lab(content: str) -> ParsedLab:
    """
    Parses a markdown lab guide into structured execution steps.
    Extracts headers, code blocks, and expected output blocks.
    """
    # Extract main title
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    lab_title = title_match.group(1).strip() if title_match else "Untitled Lab"

    # Extract overview
    overview_match = re.search(r"##\s+Overview\s*\n(.*?)(?=\n##\s+Step|\Z)", content, re.DOTALL)
    overview = overview_match.group(1).strip() if overview_match else ""

    # Split by Step headers: e.g. "## Step 1: ..."
    step_regex = r"(##\s+Step\s+(\d+):?\s*([^\n]+)\n)(.*?)(?=\n##\s+Step|\Z)"
    matches = list(re.finditer(step_regex, content, re.DOTALL))

    steps: List[LabStep] = []

    for match in matches:
        step_num = int(match.group(2))
        step_title = match.group(3).strip()
        body = match.group(4)
        raw_chunk = match.group(0)

        # Extract code block
        code_match = re.search(r"```(bash|sh|shell|python)?\n(.*?)```", body, re.DOTALL)
        command = code_match.group(2).strip() if code_match else ""
        lang = code_match.group(1) or "bash"

        # Extract description (text before code block)
        if code_match:
            desc_text = body[:code_match.start()].strip()
        else:
            desc_text = body.strip()

        # Extract expected output if present
        expected_output = None
        expected_match = re.search(r"Expected output:\s*\n(.*)", body, re.DOTALL)
        if expected_match:
            # Clean up potential trailing markdown
            expected_output = expected_match.group(1).strip()

        steps.append(
            LabStep(
                step_id=step_num,
                title=step_title,
                description=desc_text,
                command_type=lang,
                command=command,
                expected_output=expected_output,
                raw_markdown_chunk=raw_chunk,
            )
        )

    return ParsedLab(title=lab_title, overview=overview, steps=steps)
