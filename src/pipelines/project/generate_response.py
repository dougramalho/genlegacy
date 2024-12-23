from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel
from pydantic import BaseModel

class ResponseModel(BaseModel):
    loaded: bool = True

class GenerateResponse(PipelineStep):
    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        completion = self.generate_response(input_data)
        context.intermediates["loaded"] = completion.loaded
        return input_data, context, output_data
    
    def generate_response(self, data: BaseTaskInput) -> ResponseModel:
        data = ResponseModel()
        return data