from abc import ABC, abstractmethod
from typing import List
from ..engine import SemanticEntity, ParserEngine

class BaseExtractor(ABC):
    def __init__(self, engine: ParserEngine):
        self.engine = engine

    @abstractmethod
    def extract(self, file_path: str, tree: any) -> List[SemanticEntity]:
        pass
