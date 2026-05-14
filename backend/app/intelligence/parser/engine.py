import os
from typing import Dict, List, Any, Optional
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
import tree_sitter_go as tsgo
from pydantic import BaseModel

class SemanticEntity(BaseModel):
    name: str
    type: str  # e.g., "api_route", "auth_middleware", "service_call"
    file_path: str
    line_start: int
    line_end: int
    metadata: Dict[str, Any] = {}

class ParserEngine:
    def __init__(self):
        self.languages = {
            "python": Language(tspython.language()),
            "javascript": Language(tsjavascript.language()),
            "typescript": Language(tstypescript.language_typescript()),
            "tsx": Language(tstypescript.language_tsx()),
            "go": Language(tsgo.language()),
        }
        self.parser = Parser()

    def get_language(self, file_extension: str) -> Optional[str]:
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".go": "go",
        }
        return mapping.get(file_extension)

    def parse_file(self, file_path: str) -> Optional[Any]:
        _, ext = os.path.splitext(file_path)
        lang_name = self.get_language(ext)
        if not lang_name:
            return None

        lang = self.languages.get(lang_name)
        if not lang:
            return None

        self.parser.language = lang
        
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            return self.parser.parse(content)
        except Exception as e:
            # TODO: Add proper logging
            return None

    def query(self, tree: Any, query_str: str, lang_name: str) -> List[Any]:
        lang = self.languages.get(lang_name)
        if not lang:
            return []
        
        query = lang.query(query_str)
        return query.captures(tree.root_node)
