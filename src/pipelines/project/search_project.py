from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel, ProjectAnalysis
from pydantic import BaseModel
from src.utils import LLMStyleConsole
from src.services.llm_factory import LLMFactory
from src.prompts.role import BusinessAnalystPrompt


class ResponseMessageModel(BaseModel):
    content: str = None

    def __init__(self, content: str):
        super().__init__()
        self.content = content

class SearchInProjectContent(PipelineStep):

    def __init__(self):
        super().__init__()
        self.user_response = None
        self.knowledge_base = None

    def handle_response(self, response: str):  # Método de instância com self
        self.user_response = response

    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        self.knowledge_base = context.intermediates["analysis"]

        console = LLMStyleConsole(callback=self.handle_response)

        console_text = """\nO que deseja saber sobre o projeto? Agora que tenho os resources indexados, podemos explorar os dados carregados."""
        console.display_and_get_response(console_text)
        
        completion = self.search_in_contents(input_data)
        console._type_text(completion.content)

        while(True):
            console_text = """\nEm qua mais posso te ajudar?"""
            console.display_and_get_response(console_text)
            completion = self.search_in_contents(input_data)
            console._type_text(completion.content)
        
        return input_data, context, output_data
    
    def search_in_contents(self, data: BaseTaskInput) -> ResponseMessageModel:
        llm = LLMFactory("openai")
        prompt = BusinessAnalystPrompt(self.knowledge_base)

        completion = llm.create_completion(
            response_model=ProjectAnalysis,
            temperature=0,
            messages=[
                {
                    "role":"system",
                    "content": prompt.format()
                },
                {
                    "role":"user",
                    "content": self.user_response
                }
            ]
        )
        
        data = ResponseMessageModel(completion.content)
        return data
    
    