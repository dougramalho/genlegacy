from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from typing import Any, Dict, Optional
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