# src/services/project_loader/registry.py
from typing import Dict
from .base import BaseProjectLoader
from .cpp_loader import CppProjectLoader

class ProjectLoaderRegistry:
    def __init__(self):
        self._loaders: Dict[str, BaseProjectLoader] = {
            'cpp': CppProjectLoader()
        }
    
    def get_loader(self, language: str) -> BaseProjectLoader:
        loader = self._loaders.get(language)
        if not loader:
            raise ValueError(f"No loader registered for language: {language}")
        return loader