from src.pipelines.base import PipelineStep
from src.models.query import QueryInput
from src.api.models import ProcessingContext, OutputDataModel
from src.services.query.processor import QueryProcessor


class PrepareQuery(PipelineStep):
    def __init__(self):
        self.processor = QueryProcessor()
    
    def process(self, 
                input_data: QueryInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
                
        # Processa e expande a query
        query_info = self.processor.process_query(input_data.query)
        
        # Armazena todas as informações no contexto
        context.intermediates["query_info"] = query_info
        
        return input_data, context, output_data
    
class SearchVectorStore(PipelineStep):
    def __init__(self):
        self.processor = QueryProcessor()
    
    def process(self, 
                input_data: QueryInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
                
        processed_query = context.intermediates["query_info"]
        relevant_rules = self.processor.search_relevant_rules(processed_query)
        context.intermediates["relevant_rules"] = relevant_rules
        
        return input_data, context, output_data
    
class GenerateResponse(PipelineStep):
    def __init__(self):
        self.processor = QueryProcessor()
    
    def process(self, 
                input_data: QueryInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
                
        query_info = context.intermediates["query_info"]
        relevant_rules = context.intermediates["relevant_rules"]
        
        response = self.processor.generate_response(query_info, relevant_rules)
        
        # Atualiza o output_data com a resposta gerada
        output_data.answer = response["answer"]
        output_data.referenced_rules = response["referenced_rules"]
        
        # Armazena informações adicionais no contexto
        context.intermediates["suggested_followup"] = response["suggested_followup"]
        context.intermediates["rules_analyzed"] = response["rules_analyzed"]
        
        return input_data, context, output_data