# src/api/models/response_generation.py
from pydantic import BaseModel, Field
from typing import List

class GeneratedResponse(BaseModel):
    answer: str = Field(
        description="Resposta detalhada explicando as regras de negócio encontradas")
    referenced_rules: List[str] = Field(
        description="Lista de IDs das regras mencionadas na resposta")
    suggested_followup: List[str] = Field(
        description="Sugestões de perguntas relacionadas para aprofundamento",
        default_factory=list)