from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel
from src.services.project_loader.registry import ProjectLoaderRegistry
import json
from pathlib import Path

class LoadProjectV2(PipelineStep):
    def __init__(self):
        self.loader_registry = ProjectLoaderRegistry()

    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        project_path = context.intermediates["project_path"]
        language = context.intermediates["language"]
        
        # Obtém o loader apropriado
        loader = self.loader_registry.get_loader(language)
        
        # Carrega o projeto
        project_info = loader.load(project_path)
        
        # Atualiza o contexto com as informações do projeto
        context.intermediates["project_info"] = project_info
        context.intermediates["components"] = project_info['components']
        context.intermediates["build_system"] = project_info['build_system']

        json_safe_info = self._prepare_for_json(project_info)
        
        # Imprime o project_info formatado
        print("\nProject Info:")
        print(json.dumps(json_safe_info, indent=2))

        with open("data.json", "w") as arquivo:
            json.dump(json_safe_info, arquivo)
        
        return input_data, context, output_data
    
    def _prepare_for_json(self, data):
        """
        Converte estruturas de dados que não são serializáveis em JSON
        para tipos compatíveis
        """
        if isinstance(data, dict):
            return {k: self._prepare_for_json(v) for k, v in data.items()}
        elif isinstance(data, (set, list, tuple)):
            return list(self._prepare_for_json(item) for item in data)
        elif isinstance(data, Path):
            return str(data)
        else:
            return data