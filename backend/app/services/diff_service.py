import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DiffService:
    """Service for parsing and analyzing unified diffs for architectural impact."""

    @staticmethod
    def parse_diff(diff_content: str) -> List[Dict[str, Any]]:
        """Parse unified diff into a list of changed files and their hunks."""
        files = []
        current_file = None
        
        # Simple regex for unified diff parsing
        # --- a/filename
        # +++ b/filename
        file_header_re = re.compile(r'^\+\+\+ b/(.*)')
        hunk_header_re = re.compile(r'^@@ -\d+,\d+ \+(\d+),(\d+) @@')

        for line in diff_content.splitlines():
            file_match = file_header_re.match(line)
            if file_match:
                current_file = {
                    "path": file_match.group(1),
                    "hunks": []
                }
                files.append(current_file)
                continue
            
            hunk_match = hunk_header_re.match(line)
            if hunk_match and current_file:
                current_file["hunks"].append({
                    "start": int(hunk_match.group(1)),
                    "count": int(hunk_match.group(2)),
                    "lines": []
                })
                continue
            
            if current_file and current_file["hunks"]:
                current_file["hunks"][-1]["lines"].append(line)

        return files

    @staticmethod
    def get_architectural_impact(changed_files: List[Dict[str, Any]]) -> List[str]:
        """Identify files that likely impact the system architecture/security."""
        impactful_patterns = [
            r"auth",
            r"middleware",
            r"api",
            r"service",
            r"controller",
            r"security",
            r"identity",
            r"gateway",
            r"proxy",
            r"config",
            r"permission",
            r"policy"
        ]
        
        impacted_paths = []
        for file in changed_files:
            path = file["path"].lower()
            if any(re.search(pattern, path) for pattern in impactful_patterns):
                impacted_paths.append(file["path"])
                
        return impacted_paths
