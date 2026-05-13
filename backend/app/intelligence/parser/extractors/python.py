from typing import List
from .base import BaseExtractor
from ..engine import SemanticEntity

class PythonExtractor(BaseExtractor):
    def extract(self, file_path: str, tree: any) -> List[SemanticEntity]:
        entities = []
        entities.extend(self._extract_routes(file_path, tree))
        entities.extend(self._extract_service_calls(file_path, tree))
        entities.extend(self._extract_classes(file_path, tree))
        entities.extend(self._extract_functions(file_path, tree))
        return entities

    def _extract_routes(self, file_path: str, tree: any) -> List[SemanticEntity]:
        # Query for FastAPI/Flask style decorators
        query_str = """
        (decorated_definition
            decorator: (decorator
                attribute: (attribute
                    object: (identifier) @app_obj
                    attribute: (identifier) @method)
                )
            definition: (function_definition
                name: (identifier) @func_name)
        ) @route
        """
        captures = self.engine.query(tree, query_str, "python")
        
        entities = []
        # Group captures by the @route node range to avoid duplicates
        # tree-sitter query returns a list of (node, tag) tuples
        
        # Simple implementation for now
        for node, tag in captures:
            if tag == "route":
                entities.append(SemanticEntity(
                    name=f"route_{node.start_point[0]}",
                    type="api_route",
                    file_path=file_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    metadata={"language": "python"}
                ))
        return entities

    def _extract_service_calls(self, file_path: str, tree: any) -> List[SemanticEntity]:
        # Query for httpx/requests style calls
        query_str = """
        (call
            function: (attribute
                object: (identifier) @lib
                attribute: (identifier) @method)
            arguments: (argument_list
                (string) @url)
        ) @service_call
        """
        captures = self.engine.query(tree, query_str, "python")
        
        entities = []
        for node, tag in captures:
            if tag == "service_call":
                entities.append(SemanticEntity(
                    name="external_call",
                    type="service_call",
                    file_path=file_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    metadata={"language": "python"}
                ))
        return entities

    def _extract_classes(self, file_path: str, tree: any) -> List[SemanticEntity]:
        query_str = "(class_definition name: (identifier) @name) @class"
        captures = self.engine.query(tree, query_str, "python")
        entities = []
        for node, tag in captures:
            if tag == "class":
                name_node = next((n for n, t in captures if t == "name"), None)
                entities.append(SemanticEntity(
                    name=name_node.text.decode() if name_node else "UnknownClass",
                    type="class",
                    file_path=file_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    metadata={"language": "python"}
                ))
        return entities

    def _extract_functions(self, file_path: str, tree: any) -> List[SemanticEntity]:
        query_str = "(function_definition name: (identifier) @name) @func"
        captures = self.engine.query(tree, query_str, "python")
        entities = []
        for node, tag in captures:
            if tag == "func":
                name_node = next((n for n, t in captures if t == "name"), None)
                entities.append(SemanticEntity(
                    name=name_node.text.decode() if name_node else "UnknownFunc",
                    type="function",
                    file_path=file_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    metadata={"language": "python"}
                ))
        return entities
