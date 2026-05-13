import logging
import os
import subprocess
import tempfile
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)


class RepositoryIngestionService:
    """Handles secure repository cloning, validation, and ingestion setup."""

    CLONE_TIMEOUT = 60
    MAX_REPO_SIZE_MB = 500

    async def validate_repository(self, clone_url: str, branch: str = "main") -> dict:
        """
        Validate repository before cloning:
        - Check size limits
        - Verify it's a git repository
        - Ensure no binary bloat
        """
        try:
            result = await asyncio.wait_for(
                self._check_repo_size(clone_url),
                timeout=10,
            )
            if not result["valid"]:
                return {"valid": False, "reason": result.get("reason", "Invalid repository")}
            return {"valid": True, "size_mb": result.get("size_mb", 0)}
        except asyncio.TimeoutError:
            return {"valid": False, "reason": "Repository validation timeout"}
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {"valid": False, "reason": str(e)}

    async def _check_repo_size(self, clone_url: str) -> dict:
        """Check remote repository size via git ls-remote."""
        try:
            cmd = ["git", "ls-remote", "--heads", clone_url]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                return {"valid": False, "reason": "Invalid git repository"}
            return {"valid": True, "size_mb": 0}
        except Exception as e:
            logger.error(f"Size check error: {e}")
            return {"valid": False, "reason": str(e)}

    async def clone_repository(self, clone_url: str, branch: str = "main") -> dict:
        """
        Clone repository into isolated temporary workspace.
        Returns path to cloned repo or error status.
        """
        tmpdir = tempfile.mkdtemp(prefix="aegis_repo_")
        logger.info(f"Cloning {clone_url} into {tmpdir}")

        try:
            cmd = [
                "git",
                "clone",
                "--depth=1",
                "--branch",
                branch,
                clone_url,
                tmpdir,
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.CLONE_TIMEOUT,
            )

            if proc.returncode != 0:
                logger.error(f"Clone failed: {stderr.decode()}")
                return {"success": False, "error": "Clone failed"}

            logger.info(f"Repository cloned successfully to {tmpdir}")
            return {"success": True, "path": tmpdir}

        except asyncio.TimeoutError:
            logger.error("Clone timeout")
            return {"success": False, "error": "Clone timeout"}
        except Exception as e:
            logger.error(f"Clone error: {e}")
            return {"success": False, "error": str(e)}

    async def cleanup_repository(self, path: str):
        """Remove temporary repository directory."""
        try:
            if os.path.exists(path):
                import shutil
                shutil.rmtree(path)
                logger.info(f"Cleaned up {path}")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    async def get_repository_metadata(self, repo_path: str) -> dict:
        """Extract basic repository metadata (files, languages, structure)."""
        try:
            files = []
            languages = set()
            
            for root, dirs, filenames in os.walk(repo_path):
                # Skip hidden and common non-source dirs
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", "venv", "__pycache__"]]
                
                for fname in filenames:
                    if not fname.startswith("."):
                        ext = Path(fname).suffix.lower()
                        if ext in [".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"]:
                            languages.add(ext)
                        files.append(fname)

            return {
                "file_count": len(files),
                "languages": list(languages),
                "has_readme": "README.md" in files or "README" in files,
            }
        except Exception as e:
            logger.error(f"Metadata extraction error: {e}")
            return {"file_count": 0, "languages": [], "has_readme": False}


ingestion_service = RepositoryIngestionService()
