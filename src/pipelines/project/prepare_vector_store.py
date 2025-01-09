# src/pipelines/steps/prepare_vector_store.py
from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel
from src.repositories.vector_store.store import VectorStore
from pathlib import Path
import json

class PrepareVectorStore(PipelineStep):
    def __init__(self):
        self.vector_store = VectorStore()
    
    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        rules = context.intermediates.get("enriched_business_rules", [])
        
        # Prepara embeddings e armazena
        self.vector_store.store_rules(rules)
        
        # Adiciona referência da vector store ao contexto
        context.intermediates["vector_store"] = self.vector_store

        # json_safe_info = self._prepare_for_json(rules)
        # with open("data.json", "w") as arquivo:
        #     json.dump(json_safe_info, arquivo)
        # Diagnóstico após armazenamento
        stats = self.vector_store.get_collection_stats()
        print("\nVector Store Stats:")
        print(f"Total records: {stats['total_records']}")
        if stats.get('sample'):
            print("\nSample record:")
            print(json.dumps(stats['sample'], indent=2))
            
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