from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from typing import Any, Dict, Optional, List
from enum import Enum
from typing_extensions import Annotated
from instructor import llm_validator
from datetime import datetime

class ProcessCategory(str, Enum):
    """Enumeration of process categories for incoming requests"""
    GENERAL = "general"
    PROJECT_DISCOVERY = "project-discovery"
    OTHER = "other"

# Base Task Classes
class BaseTaskInput(BaseModel):
    command_name: str
    
    def to_dict(self) -> dict:
        return self.model_dump()
    
class WelcomeTaskInput(BaseTaskInput):
    command_name: str = "welcome"

class DiscoveryTaskInput(BaseTaskInput):
    command_name: str = "discovery"
    topic: ProcessCategory
    project_details: Optional[Dict[str, Any]] = None

class QueryTaskInput(BaseTaskInput):
    command_name: str = "query"
    query: str

# Other Models
class ProcessingContext(BaseModel):
    parameters: Dict[str, Any] = Field(default_factory=dict)
    intermediates: Dict[str, Any] = Field(default_factory=dict)

class OutputDataModel(BaseModel):
    result: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskResult(BaseModel):
    task_id: Optional[str] = None
    status: str
    input_data: BaseTaskInput
    processing_context: ProcessingContext
    output_data: Optional[OutputDataModel] = None
    created_at: datetime = datetime.now()

class EventModel(BaseModel):
    event_type: str
    data: BaseTaskInput

class ProjectAnalysis(BaseModel):
    content: str = Field(description="Analysis content")
    
class Reply(BaseModel):
    content: str = Field(description="Your reply that we send to the customer.")
    category: ProcessCategory = Field(
        description="Correctly assign one of the predefined categories"
    )
    confidence: float = Field(
        ge=0, le=1, description="Confidence in the category prediction."
    )


class BusinessRuleAnalysis(BaseModel):
    rule_id: str = Field(description="ID da regra analisada")
    is_business_rule: bool = Field(
        description="Indica se é realmente uma regra de negócio")
    description: str = Field(
        description="Descrição em linguagem natural do que a regra faz")
    dependencies: List[str] = Field(
        default_factory=list,
        description="IDs de outras regras que esta regra depende ou se relaciona")
    rule_type: str = Field(
        description="Tipo da regra: 'validation', 'calculation', 'process', ou 'business_logic'")
    domain_objects: List[str] = Field(
        default_factory=list,
        description="Nomes dos objetos de domínio afetados pela regra")
    business_impact: str = Field(
        description="Descrição do impacto de negócio desta regra")
    confidence_score: float = Field(
        ge=0, 
        le=1,
        description="Nível de confiança na classificação da regra (0.0 a 1.0)")

class BusinessRulesAnalysis(BaseModel):
    """Lista de análises das regras de negócio encontradas no código."""
    analyses: List[BusinessRuleAnalysis] = Field(
        description="Lista de análises de regras de negócio")
    
# class EnrichedBusinessRule(BaseModel):
#     is_business_rule: bool = Field(
#         description="Indica se é realmente uma regra de negócio")
#     description: str = Field(
#         description="Descrição em linguagem natural do que a regra faz")
#     dependencies: List[str] = Field(
#         default_factory=list,
#         description="IDs de outras regras que esta regra depende ou se relaciona")
#     rule_type: str = Field(
#         description="Tipo da regra: 'validation', 'calculation', 'process', ou 'business_logic'")
#     domain_objects: List[str] = Field(
#         default_factory=list,
#         description="Nomes dos objetos de domínio afetados pela regra")
#     business_impact: str = Field(
#         description="Descrição do impacto de negócio desta regra")
#     confidence_score: float = Field(
#         ge=0, 
#         le=1,
#         description="Nível de confiança na classificação da regra (0.0 a 1.0)")

# class BusinessRulesAnalysis(BaseModel):
#     """Análise das regras de negócio encontradas no código."""
#     rules: Dict[str, EnrichedBusinessRule] = Field(
#         description="Dicionário onde a chave é o ID da regra e o valor é a análise detalhada da regra")