from src.api.models import (
    BaseTaskInput, 
    TaskResult, 
    ProcessingContext,
    OutputDataModel
)
from src.pipelines.registry import PipelineRegistry
import uuid

def process_task(task_input: BaseTaskInput) -> dict:
    pipeline = PipelineRegistry.get_pipeline(task_input)
    processing_context, output_data = pipeline.run(task_input)

    # Verifica se processing_context e output_data já são instâncias das classes corretas
    if not isinstance(processing_context, ProcessingContext):
        processing_context = ProcessingContext(**processing_context)
    
    if not isinstance(output_data, OutputDataModel):
        output_data = OutputDataModel(**output_data)

    task_result = TaskResult(
        task_id=str(uuid.uuid4()),
        status="completed",
        input_data=task_input,
        processing_context=processing_context,  # Não usa mais **
        output_data=output_data  # Não usa mais **
    )
    
    print("Task completed successfully!")
    return task_result.model_dump()