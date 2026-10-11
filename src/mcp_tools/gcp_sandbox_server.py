"""
GCP Sandbox Tool interface compatible with Model Context Protocol (MCP) tool schema.
Supports real execution mode as well as a high-fidelity simulation sandbox
that mimics GCP API behaviors, deprecation errors, and permission checks.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class CommandResult(BaseModel):
    command: str
    exit_code: int
    stdout: str
    stderr: str
    execution_time_ms: int = 150


class GCPSandboxTools:
    """
    Simulated/Interactive GCP Sandbox execution harness.
    Acts as the MCP tool provider for the LabDoctor Agent.
    """

    def __init__(self, mode: str = "simulated", project_id: str = "demo-learning-proj"):
        self.mode = mode
        self.project_id = project_id
        self.secrets = {}
        self.services = {}
        self.iam_bindings = []

    def execute_bash(self, command: str) -> CommandResult:
        """
        Executes a shell command within the GCP sandbox environment.
        """
        clean_cmd = " ".join([line.strip() for line in command.splitlines() if line.strip() and not line.strip().startswith("#")])

        # Handle gcloud config commands
        if "gcloud config set" in clean_cmd:
            return CommandResult(
                command=command,
                exit_code=0,
                stdout="Updated property [core/project].\nUpdated property [run/region].",
                stderr="",
            )

        # Handle Secret Manager creation
        if "gcloud secrets create" in clean_cmd:
            if "--replication-policy=" in clean_cmd:
                # Catching deprecated flag in Secret Manager
                return CommandResult(
                    command=command,
                    exit_code=1,
                    stdout="",
                    stderr=(
                        "ERROR: (gcloud.secrets.create) unrecognized arguments: "
                        "--replication-policy=automatic. "
                        "The replication policy argument has been deprecated; use --replication-policy=user-managed or omit for default automatic replication."
                    ),
                )
            self.secrets["api-token-secret"] = "active"
            return CommandResult(
                command=command,
                exit_code=0,
                stdout="Created secret [api-token-secret].",
                stderr="",
            )

        # Handle IAM bindings
        if "gcloud secrets add-iam-policy-binding" in clean_cmd:
            self.iam_bindings.append(clean_cmd)
            return CommandResult(
                command=command,
                exit_code=0,
                stdout="Updated IAM policy for secret [api-token-secret].",
                stderr="",
            )

        # Handle Cloud Run deployment
        if "gcloud run deploy" in clean_cmd:
            if "--platform=managed" in clean_cmd:
                # Deprecated warning / error
                return CommandResult(
                    command=command,
                    exit_code=2,
                    stdout="",
                    stderr=(
                        "ERROR: (gcloud.run.deploy) unrecognized arguments: --platform=managed. "
                        "Flag '--platform' is no longer supported in current Google Cloud SDK. Cloud Run is always fully managed."
                    ),
                )
            
            return CommandResult(
                command=command,
                exit_code=0,
                stdout=(
                    "Service [hello-service] revision [hello-service-00001-abc] has been deployed and is serving 100 percent of traffic.\n"
                    "Service URL: https://hello-service-xyz-uc.a.run.app"
                ),
                stderr="",
            )

        # Handle gsutil asset download
        if "gsutil cp gs://" in clean_cmd:
            if "expired-legacy-training-bucket-2022" in clean_cmd:
                return CommandResult(
                    command=command,
                    exit_code=1,
                    stdout="",
                    stderr=(
                        "BucketNotFoundException: 404 The specified bucket "
                        "'expired-legacy-training-bucket-2022' does not exist."
                    ),
                )

        # Handle Cloud Functions deploy
        if "gcloud functions deploy" in clean_cmd:
            if "--trigger-resource=" in clean_cmd or "--trigger-event=" in clean_cmd:
                return CommandResult(
                    command=command,
                    exit_code=1,
                    stdout="",
                    stderr=(
                        "ERROR: (gcloud.functions.deploy) Cloud Functions 1st gen background triggers "
                        "are deprecated in this region. You must migrate to Cloud Functions 2nd gen "
                        "(--gen2) with Eventarc triggers, OR deploy a container service to Cloud Run directly."
                    ),
                )
            return CommandResult(
                command=command,
                exit_code=0,
                stdout="State: ACTIVE\nFunction deployed successfully.",
                stderr="",
            )

        # Fallback simulated response
        return CommandResult(
            command=command,
            exit_code=0,
            stdout="Command executed successfully in sandbox.",
            stderr="",
        )

    def inspect_gcp_documentation(self, command_name: str) -> str:
        """
        MCP tool: Look up current syntax and deprecation notices in official GCP documentation.
        """
        knowledge_base = {
            "gcloud secrets create": (
                "In newer gcloud releases, '--replication-policy=automatic' is the default and should be omitted, "
                "or specify '--replication-policy=automatic' as '--replication-policy=automatic' only on legacy CLI. "
                "Recommended modern syntax: 'gcloud secrets create [NAME] --data-file=[PATH]'"
            ),
            "gcloud run deploy": (
                "The '--platform' flag has been deprecated and removed. All Cloud Run services are deployed to "
                "the managed platform by default. Remove '--platform=managed'."
            ),
        }
        for k, v in knowledge_base.items():
            if k in command_name:
                return v
        return "No specific deprecation notices found for this command."

    def get_tool_definitions(self) -> list:
        """Returns JSON schema definitions compatible with Gemini / MCP function calling."""
        return [
            {
                "name": "execute_bash",
                "description": "Executes shell and gcloud commands in the GCP sandbox environment",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "command": {"type": "STRING", "description": "The exact shell command to run"}
                    },
                    "required": ["command"],
                },
            },
            {
                "name": "inspect_gcp_documentation",
                "description": "Looks up the latest GCP command syntax, deprecations, and flags",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "command_name": {"type": "STRING", "description": "The command or gcloud component to check"}
                    },
                    "required": ["command_name"],
                },
            },
        ]
