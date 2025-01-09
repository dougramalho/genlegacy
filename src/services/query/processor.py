# src/services/query/processor.py
from typing import List, Dict, Any
from src.services.llm_factory import LLMFactory
from src.repositories.vector_store.store import VectorStore
from src.prompts.role import QueryExpansionPrompt
from src.models.query_expansion import QueryExpansion
from src.models.response_generation import GeneratedResponse
from src.prompts.role import ResponseGenerationPrompt

class QueryProcessor:
    def __init__(self):
        self.llm_client = LLMFactory("openai")
        self.vector_store = VectorStore()
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Expande e processa a query para melhorar a busca
        """
        # Cria o prompt para expansão
        prompt = QueryExpansionPrompt(query)
        
        content = prompt.format()

        # Obtém a expansão da query via LLM
        expansion = self.llm_client.create_completion(
            response_model=QueryExpansion,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em análise de código e regras de negócio."
                },
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        
        # Combina os termos de busca em uma única query para a vector store
        search_query = self._build_search_query(expansion)
        
        return {
            "original_query": query,
            "expanded_query": expansion.expanded_query,
            "search_query": search_query,
            "search_terms": expansion.search_terms,
            "domain_focus": expansion.domain_focus
        }
    
    def _build_search_query(self, expansion: QueryExpansion) -> str:
        """
        Constrói a query final para a vector store combinando os diferentes aspectos
        """
        components = [
            expansion.expanded_query,
            " ".join(expansion.search_terms),
            " ".join(expansion.domain_focus)
        ]
        
        return " ".join(components)

    def search_relevant_rules(self, query_info: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca regras relevantes usando a query expandida
        """
        results = self.vector_store.search_similar_rules(
            query_info["search_query"], 
            top_k=limit
        )
        
        # Adiciona informação da query expandida aos resultados
        for result in results:
            result["query_info"] = {
                "original_query": query_info["original_query"],
                "expanded_query": query_info["expanded_query"],
                "domain_focus": query_info["domain_focus"]
            }
        
        return results
    
    def generate_response(self, query_info: Dict[str, Any], relevant_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera uma resposta contextualizada baseada nas regras encontradas
        """
        # Criar o prompt para geração de resposta
        prompt = ResponseGenerationPrompt(query_info, relevant_rules)

        content = prompt.format()
        
        # Gerar a resposta usando o LLM
        response = self.llm_client.create_completion(
            response_model=GeneratedResponse,
            temperature=0.7,  # Um pouco mais alto para respostas mais naturais
            messages=[
                {
                    "role": "system",
                    "content": """Você é um especialista em análise de código e regras de negócio.
                    Seu objetivo é explicar regras de negócio de forma clara e precisa,
                    relacionando diferentes partes do código quando relevante."""
                },
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        
        return {
            "answer": response.answer,
            "referenced_rules": response.referenced_rules,
            "suggested_followup": response.suggested_followup,
            "query_info": query_info,
            "rules_analyzed": len(relevant_rules)
        }