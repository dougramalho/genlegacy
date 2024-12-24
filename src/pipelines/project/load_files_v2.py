from src.pipelines.base import PipelineStep
from src.api.models import DiscoveryTaskInput, ProcessingContext, OutputDataModel
from pydantic import BaseModel
from src.utils import LLMStyleConsole
import os
from src.services.llm_factory import LLMFactory
from src.prompts.role import CPlusPlusInfoPrompt
from src.api.models import ProjectAnalysis

class LoadFilesV2(PipelineStep):

    def __init__(self):
        super().__init__()
        self.project_path = None
        self.content = None

    def handle_response(self, response: str):  # Método de instância com self
        self.project_path = response

    def process(self, 
                input_data: DiscoveryTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        console = LLMStyleConsole()
        console_text = f"Certo, então vamos falar sobre: {input_data.topic}"
        console._type_text(console_text)

        console_text = f"Podemos começar carregando o projeto em memória para que eu possa criar o contexto do projeto."
        console._type_text(console_text)

        console_text = f"Me informe o caminho para a pasta raíz do repositório"
        console.display_and_get_response(console_text, callback=self.handle_response)

        context.intermediates["project_path"] = self.project_path

        return input_data, context, output_data