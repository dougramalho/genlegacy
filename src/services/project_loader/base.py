from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class BaseProjectLoader(ABC):
    @abstractmethod
    def load(self, project_path: str) -> Dict[str, Any]:
        """
        Carrega o projeto e retorna suas informações estruturadas
        """
        pass