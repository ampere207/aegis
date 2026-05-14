from abc import ABC, abstractmethod
from typing import List
from ..engine import SemanticEntity, ParserEngine

class BaseExtractor(ABC):
    def __init__(self, engine: ParserEngine):
        self.engine = engine

    @abstractmethod
    def extract(self, file_path: str, tree: any) -> List[SemanticEntity]:
        pass
    def _extract_generic_blocks(self, file_path: str, node: any, entities: List[SemanticEntity], depth: int = 0) -> None:
        """Recursively find significant blocks if no specific entities were found."""
        if depth > 5: return # Avoid too much noise
        
        # Look for assignments, calls, or branches at this level
        if node.type in ["expression_statement", "assignment", "if_statement", "for_statement", "while_statement"]:
            # Only record if it's large enough to be 'significant'
            if (node.end_point[0] - node.start_point[0]) > 2:
                entities.append(SemanticEntity(
                    name=f"logic_block_{node.start_point[0]}",
                    type="logic_block",
                    file_path=file_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                    metadata={"node_type": node.type}
                ))
                return # Don't recurse into our own captured block

        for child in node.children:
            self._extract_generic_blocks(file_path, child, entities, depth + 1)
