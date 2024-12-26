class VectorStore:
    def __init__(self):
        self.rules = []
        self.embeddings = {}
    
    def store_rules(self, rules):
        # TODO: Implementar a criação real dos embeddings
        self.rules = rules
        
    def search_similar(self, query, top_k=5):
        # TODO: Implementar busca por similaridade
        pass