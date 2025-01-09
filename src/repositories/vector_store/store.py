# src/services/vector_store/store.py
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
import json
import hashlib
from src.config.settings import OPENAI_API_KEY

class VectorStore:
    def __init__(self):
        # Inicializa o client do Chroma
        self.client = chromadb.Client()
        
        # Usa o embedding function da OpenAI
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name="text-embedding-ada-002"
        )
        
        # Cria ou obtém a collection
        self.collection = self.client.get_or_create_collection(
            name="business_rules",
            embedding_function=self.embedding_function,
            metadata={"description": "Business rules extracted from code"}
        )

    def store_rules(self, rules: List[Dict[str, Any]]):
        """
        Armazena as regras de negócio na vector store
        """
        documents = []  # Texto para embedding
        metadatas = []  # Metadados associados
        ids = []        # IDs únicos
        
        for rule in rules:
            # Prepara o texto para embedding combinando informações relevantes
            rule_text = self._prepare_rule_text(rule)
            
            # Prepara metadados
            metadata = {
                'rule_id': rule['id'],
                'function_name': rule['function_name'],
                'type': rule.get('type', ''),
                'confidence': rule.get('confidence', ''),
                'confidence_score': rule.get('confidence_score', 0.0),
                'dependencies': json.dumps(rule.get('dependencies', [])),
                'domain_objects': json.dumps(rule.get('domain_objects', [])),
                'business_impact': rule.get('business_impact', ''),
                'description': rule.get('description', '')
            }
            
            # Gera um ID único baseado no conteúdo
            unique_id = self._generate_unique_id(rule['id'], rule['content'])
            
            documents.append(rule_text)
            metadatas.append(metadata)
            ids.append(unique_id)
        
        # Armazena no Chroma
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def _prepare_rule_text(self, rule: Dict[str, Any]) -> str:
        """
        Prepara o texto que será usado para gerar o embedding
        """
        components = [
            f"Function: {rule['function_name']}",
            f"Description: {rule.get('description', '')}",
            f"Type: {rule.get('type', '')}",
            f"Business Impact: {rule.get('business_impact', '')}",
            "Code:",
            rule.get('content', '')
        ]
        
        return "\n".join(components)

    def _generate_unique_id(self, rule_id: str, content: str) -> str:
        """
        Gera um ID único baseado no ID da regra e seu conteúdo
        """
        combined = f"{rule_id}_{content}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    def search_similar_rules(self, query: str, top_k: int = 5):
        """
        Busca regras similares baseado em uma query
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )
        
        return self._process_search_results(results)

    def _process_search_results(self, results):
        """
        Processa os resultados da busca
        """
        processed_results = []
        
        for i, metadata in enumerate(results['metadatas'][0]):
            processed_results.append({
                'metadata': {
                    **metadata,
                    'dependencies': json.loads(metadata['dependencies']),
                    'domain_objects': json.loads(metadata['domain_objects'])
                },
                'content': results['documents'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return processed_results
    
    def get_collection_stats(self) -> dict:
        """
        Retorna estatísticas sobre a collection
        """
        try:
            collection = self.collection
            count = collection.count()
            
            # Pega uma amostra de registros se existirem
            sample = None
            if count > 0:
                sample = collection.get(limit=1)
            
            return {
                "collection_name": "business_rules",
                "total_records": count,
                "sample": sample
            }
        except Exception as e:
            return {
                "error": f"Error getting collection stats: {str(e)}"
            }

    def list_all_rules(self, limit: int = 10) -> list:
        """
        Lista todas as regras armazenadas
        """
        try:
            collection = self.collection
            results = collection.get(
                include=["metadatas", "documents", "embeddings"],
                limit=limit
            )
            
            return {
                "total": collection.count(),
                "results": results
            }
        except Exception as e:
            return {
                "error": f"Error listing rules: {str(e)}"
            }