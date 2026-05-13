from typing import List
from .base import BaseExtractor
from ..engine import SemanticEntity

class TypeScriptExtractor(BaseExtractor):
    def extract(self, file_path: str, tree: any) -> List[SemanticEntity]:
        entities = []
        entities.extend(self._extract_express_routes(file_path, tree))
        entities.extend(self._extract_classes(file_path, tree))
        entities.extend(self._extract_functions(file_path, tree))
        return entities

    def _extract_express_routes(self, file_path: str, tree: any) -> List[SemanticEntity]:
        # Query for express style routes: app.get('/path', ...)
        query_str = """
        (call_expression
            function: (member_expression
                object: (identifier) @app
                property: (property_identifier) @method
                (#match? @method "^(get|post|put|delete|patch)$")
            )
            arguments: (arguments
                (string) @path
            )
        ) @route
        """
        captures = self.engine.query(tree, query_str, "typescript")
        
        entities = []
        for node, tag in captures:
            if tag == "route":
                entities.append(SemanticEntity(
                    name=f"express_route_{node.start_point[0]}",
                    type="api_route",
                    file_path=file_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    metadata={"language": "typescript"}
                ))
        return entities

    def _extract_classes(self, file_path: str, tree: any) -> List[SemanticEntity]:
        query_str = "(class_declaration name: (identifier) @name) @class"
        captures = self.engine.query(tree, query_str, "typescript")
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
                    metadata={"language": "typescript"}
                ))
        return entities

    def _extract_functions(self, file_path: str, tree: any) -> List[SemanticEntity]:
        query_str = "(function_declaration name: (identifier) @name) @func"
        captures = self.engine.query(tree, query_str, "typescript")
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
                    metadata={"language": "typescript"}
                ))
        return entities
