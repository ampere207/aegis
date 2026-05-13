import logging
from typing import List, Dict, Any
from ..services.github_client import GitHubClient
from ..services.diff_service import DiffService
from .pipeline import AnalysisPipeline
from ..core.config import settings

logger = logging.getLogger(__name__)

class PRAnalyzer:
    """Orchestrator for Pull Request security and architectural analysis."""

    def __init__(self):
        self.github_client = GitHubClient()
        self.diff_service = DiffService()

    async def analyze_pr(
        self, 
        owner: str, 
        repo: str, 
        pr_number: int, 
        access_token: str,
        repo_id: int
    ) -> Dict[str, Any]:
        """Perform a deep architectural analysis of a pull request."""
        logger.info(f"Starting PR analysis for {owner}/{repo} PR #{pr_number}")
        
        # 1. Fetch Diff
        diff_content = await self.github_client.get_pull_request_diff(owner, repo, pr_number, access_token)
        if not diff_content:
            return {"error": "Could not fetch PR diff"}

        # 2. Parse and Identify Impact
        changed_files = self.diff_service.parse_diff(diff_content)
        impacted_paths = self.diff_service.get_architectural_impact(changed_files)
        
        logger.info(f"PR #{pr_number} impacts {len(impacted_paths)} architectural files")

        # 3. Graph Delta Reasoning (Phase 3 Core)
        # We'll use the existing AI reasoning engine but with a PR-specific prompt
        # and focused context (only changed files + their direct dependencies)
        
        findings = await self._run_ai_pr_review(impacted_paths, diff_content)
        
        return {
            "pr_number": pr_number,
            "impacted_files": impacted_paths,
            "findings": findings,
            "summary": self._generate_summary(impacted_paths, findings)
        }

    async def _run_ai_pr_review(self, impacted_paths: List[str], diff_content: str) -> List[Dict[str, Any]]:
        """Run a specialized Gemini prompt for PR architectural review."""
        if not settings.GEMINI_API_KEY:
            return [{"title": "AI Disabled", "description": "Set GEMINI_API_KEY for PR reviews"}]

        # For Phase 3, we'll implement a focused prompt
        # In a real implementation, we would pull the graph deltas here
        # For now, we'll pass the diff summary to Gemini
        
        # Placeholder for AI logic (simulating the call for now)
        return [
            {
                "title": "Architectural Trust Boundary Change",
                "description": f"The changes in {impacted_paths[0] if impacted_paths else 'this PR'} appear to modify how services authenticate. Ensure downstream validation is still enforced.",
                "severity": "medium",
                "type": "trust_boundary"
            }
        ]

    def _generate_summary(self, impacted_paths: List[str], findings: List[Dict[str, Any]]) -> str:
        if not impacted_paths:
            return "This PR does not appear to impact core architectural components."
        
        return f"Architectural impact detected in {len(impacted_paths)} files. Found {len(findings)} potential security considerations."
