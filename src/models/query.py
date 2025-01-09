# src/api/models/query.py
from pydantic import BaseModel, Field
from typing import List, Optional

class QueryInput(BaseModel):
    query: str = Field(description="Pergunta do desenvolvedor sobre as regras de negócio")

class QueryContext(BaseModel):
    processed_query: str = Field(description="Query processada e expandida")
    relevant_rules: List[dict] = Field(description="Regras relevantes encontradas")
    
class QueryResponse(BaseModel):
    answer: str = Field(description="Resposta formatada para o desenvolvedor")
    referenced_rules: List[str] = Field(description="IDs das regras mencionadas na resposta")