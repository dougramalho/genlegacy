from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel
from pydantic import BaseModel
from src.utils import LLMStyleConsole
import os
from src.services.llm_factory import LLMFactory
from src.prompts.role import CPlusPlusInfoPrompt
from src.api.models import ProjectAnalysis


class ResponseProjectAnalysisModel(BaseModel):
    analysis: str = None

    def __init__(self, analysis: str):
        super().__init__()
        self.analysis = analysis

class ResponseProjectContentModel(BaseModel):
    content: str = None

    def __init__(self, content: str):
        super().__init__()
        self.content = content

class LoadProject(PipelineStep):

    def __init__(self):
        super().__init__()
        self.project_path = None
        self.content = None

    def handle_response(self, response: str):  # Método de instância com self
        self.project_path = response

    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        console = LLMStyleConsole()
        console_text = f"Certo, então vamos falar sobre: {input_data.topic}"
        console._type_text(console_text)

        console_text = f"Podemos começar carregando o projeto em memória para que eu possa criar o contexto do projeto."
        console._type_text(console_text)

        console_text = f"Me informe o caminho para a pasta raíz do repositório"
        console.display_and_get_response(console_text, callback=self.handle_response)

        console_text = f"Vou processar os resources do projeto, isso pode demorar um pouco :("
        console._type_text(console_text)

        routeCompletion = self.route_pipeline(input_data)
        context.intermediates["project_path"] = self.project_path
        context.intermediates["project_content"] = routeCompletion.content

        completion = self.resume_project(input_data)
        context.intermediates["analysis"] = completion.analysis

        console._type_text(completion.analysis)

        return input_data, context, output_data
    
    def resume_project(self, data: BaseTaskInput) -> ResponseProjectAnalysisModel:
        llm = LLMFactory("openai")
        prompt = CPlusPlusInfoPrompt()

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
                    "content": self.content
                }
            ]
        )

        data = ResponseProjectAnalysisModel(completion.content)
        return data
    
    def route_pipeline(self, data: BaseTaskInput) -> ResponseProjectContentModel:

        target_files = ['main.cpp', 'menu.cpp', 'business.cpp']
        self.content = ""

        if not os.path.exists(self.project_path):
            raise Exception(f"O caminho {self.project_path} não existe")
        
        for filename in target_files:
            file_path = os.path.join(self.project_path, filename)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        # Adiciona marcadores de início e fim do arquivo
                        self.content += f"\n--- Início do arquivo {filename} ---\n"
                        self.content += file.read()
                        self.content += f"\n--- Fim do arquivo {filename} ---\n"
                except Exception as e:
                    print(f"Erro ao ler o arquivo {filename}: {str(e)}")
            else:
                print(f"Arquivo {filename} não encontrado em {self.project_path}")

        data = ResponseProjectContentModel(self.content)
        return data