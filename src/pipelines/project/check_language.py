from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel
from pydantic import BaseModel

class ResponseCheckLanguageModel(BaseModel):
    loaded: bool = True

class CheckLanguage(PipelineStep):
    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        completion = self.check_language(input_data)
        context.intermediates["loaded"] = completion.loaded
        return input_data, context, output_data
    
    def check_language(self, data: BaseTaskInput) -> ResponseCheckLanguageModel:
        data = ResponseCheckLanguageModel()
        return data