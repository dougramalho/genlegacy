# src/api/models/query_expansion.py
from pydantic import BaseModel, Field
from typing import List

class QueryExpansion(BaseModel):
    expanded_query: str = Field(
        description="Versão expandida e detalhada da query original")
    search_terms: List[str] = Field(
        description="Termos chave para busca na vector store",
        default_factory=list)
    domain_focus: List[str] = Field(
        description="Objetos de domínio relevantes para a busca",
        default_factory=list)