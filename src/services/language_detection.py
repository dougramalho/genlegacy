from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel
import os


class ResponseCheckLanguageModel(BaseModel):
    language: str
    confidence: float
    detected_files: Dict[str, int]  # extensão -> contagem
    main_files: List[str]  # arquivos principais encontrados (CMakeLists.txt, etc)
    
class LanguageDetectionStrategy:
    def __init__(self):
        self.language_patterns = {
            'cpp': {
                'extensions': ['.cpp', '.hpp', '.h', '.cc', '.cxx', '.hxx'],
                'config_files': ['CMakeLists.txt', 'Makefile', '.clang-format'],
                'weight': {
                    '.cpp': 1.0,
                    '.hpp': 0.8,
                    '.h': 0.6,
                    '.cc': 1.0,
                    '.cxx': 1.0,
                    '.hxx': 0.8
                }
            }
            # Podemos adicionar outros padrões aqui posteriormente
        }

    def detect(self, project_path: str) -> ResponseCheckLanguageModel:
        path = Path(project_path)
        if not path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        # Coleta informações sobre arquivos
        file_counts: Dict[str, int] = {}
        main_files: List[str] = []
        
        # Percorre todos os arquivos do projeto
        for root, _, files in os.walk(project_path):
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                
                # Conta extensões
                if ext:
                    file_counts[ext] = file_counts.get(ext, 0) + 1
                
                # Verifica arquivos de configuração
                if file in self.language_patterns['cpp']['config_files']:
                    main_files.append(file)

        # Calcula score para C++
        cpp_score = 0.0
        if file_counts:
            for ext, count in file_counts.items():
                if ext in self.language_patterns['cpp']['weight']:
                    cpp_score += count * self.language_patterns['cpp']['weight'][ext]

        # Normaliza o score (0 a 1)
        total_files = sum(file_counts.values())
        confidence = cpp_score / total_files if total_files > 0 else 0.0

        # Determina a linguagem baseado nos scores
        language = 'cpp' if confidence > 0.5 else 'unknown'

        return ResponseCheckLanguageModel(
            language=language,
            confidence=confidence,
            detected_files=file_counts,
            main_files=main_files
        )
