from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel
from pydantic import BaseModel

class LoadResponseModel(BaseModel):
    loaded: bool = True

class LoadFiles(PipelineStep):
    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        completion = self.load_files(input_data)
        context.intermediates["loaded"] = completion.loaded
        return input_data, context, output_data
    
    def load_files(self, data: BaseTaskInput) -> LoadResponseModel:
        data = LoadResponseModel()
        return data