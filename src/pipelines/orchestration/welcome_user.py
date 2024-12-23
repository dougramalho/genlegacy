from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel
from pydantic import BaseModel
from src.utils import LLMStyleConsole

class ResponseCheckLanguageModel(BaseModel):
    loaded: bool = True

class WelcomeUser(PipelineStep):

    def __init__(self):
        super().__init__()
        self.user_response = None

    def handle_response(self, response: str):  # Método de instância com self
        self.user_response = response

    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        console = LLMStyleConsole(callback=self.handle_response)

        welcome_text = """Olá! Sou seu assistente pessoal de desenvolvimento. \nQual nosso desafio de hoje?"""

        console.display_and_get_response(welcome_text)
        
        completion = self.check_language(input_data)
        context.intermediates["message"] = self.user_response
        
        return input_data, context, output_data
    
    def check_language(self, data: BaseTaskInput) -> ResponseCheckLanguageModel:
        data = ResponseCheckLanguageModel()
        return data
    
    