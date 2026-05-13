import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple


class IngestManager:
    BASE_DIR = Path("/tmp/aegis_ingest")

    @classmethod
    def _ensure_base(cls):
        cls.BASE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def create_workspace(cls, repo_full_name: str) -> Path:
        cls._ensure_base()
        safe_name = repo_full_name.replace("/", "_")
        ws = cls.BASE_DIR / f"{safe_name}_{os.getpid()}"
        ws.mkdir(parents=True, exist_ok=True)
        return ws

    @classmethod
    def shallow_clone(cls, repo_url: str, dest: Path, timeout: int = 30) -> Tuple[bool, str]:
        """Perform a shallow `git clone --depth 1` into dest. Returns (ok, message)."""
        try:
            cmd = ["git", "clone", "--depth", "1", "--no-single-branch", repo_url, str(dest)]
            subprocess.run(cmd, check=True, timeout=timeout)
            return True, "cloned"
        except subprocess.CalledProcessError as e:
            return False, f"git failed: {e}"
        except subprocess.TimeoutExpired:
            return False, "clone timeout"

    @classmethod
    def validate_workspace(cls, dest: Path, max_bytes: int = 200 * 1024 * 1024) -> Tuple[bool, str]:
        """Check approximate workspace size and basic file heuristics."""
        total = 0
        for root, _, files in os.walk(dest):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                    if total > max_bytes:
                        return False, "repo too large"
                except OSError:
                    continue
        return True, "ok"

    @classmethod
    def cleanup_workspace(cls, dest: Path):
        try:
            shutil.rmtree(dest)
        except Exception:
            pass
