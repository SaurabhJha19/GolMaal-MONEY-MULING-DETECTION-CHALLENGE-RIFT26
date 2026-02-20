from abc import ABC, abstractmethod
from typing import List
from app.models.detection import DetectionResult
import networkx as nx


class BaseDetector(ABC):

    @abstractmethod
    def detect(self, graph: nx.MultiDiGraph) -> List[DetectionResult]:
        pass
