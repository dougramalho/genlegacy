from src.pipelines.base import BasePipeline
from .steps import PrepareQuery, SearchVectorStore, GenerateResponse

class QueryPipeline(BasePipeline):
    def __init__(self):
        super().__init__()
        self.add_step(PrepareQuery())
        self.add_step(SearchVectorStore())
        self.add_step(GenerateResponse())