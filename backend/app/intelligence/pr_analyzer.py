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

        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage, SystemMessage
        import json

        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1
        )

        system_prompt = """
        You are a Senior Security Architect. Analyze the provided Git diff for architectural security risks.
        Focus on:
        - Changes to auth logic, middleware, or decorators.
        - Modifications to trust boundaries or external API calls.
        - New dependencies or sensitive data handling.
        
        Return ONLY a JSON array of findings. Each finding must have:
        { "title": "...", "description": "...", "severity": "high/medium/low", "type": "..." }
        """

        user_prompt = f"""
        Impacted Architectural Files: {impacted_paths}
        
        Diff Content:
        {diff_content[:10000]} # Truncate if too large
        
        Perform a deep security review.
        """

        try:
            response = await llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Extract JSON from response
            text = response.content
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            findings = json.loads(text)
            return findings
        except Exception as e:
            logger.error(f"AI PR Review failed: {e}")
            return [{
                "title": "AI Analysis Failed",
                "description": f"Could not perform deep reasoning: {str(e)}",
                "severity": "medium",
                "type": "error"
            }]

    def _generate_summary(self, impacted_paths: List[str], findings: List[Dict[str, Any]]) -> str:
        if not impacted_paths:
            return "This PR does not appear to impact core architectural components."
        
        return f"Architectural impact detected in {len(impacted_paths)} files. Found {len(findings)} potential security considerations."
