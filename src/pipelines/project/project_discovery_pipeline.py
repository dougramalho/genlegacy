from src.pipelines.project.check_language import CheckLanguage
from src.pipelines.project.load_files import LoadFiles
from src.pipelines.project.generate_response import GenerateResponse
from src.pipelines.base import BasePipeline
from src.pipelines.project.load_project import LoadProject
from src.pipelines.project.load_project_v2 import LoadProjectV2
from src.pipelines.project.search_project import SearchInProjectContent
from src.pipelines.project.load_files_v2 import LoadFilesV2
from src.pipelines.project.identify_business_rules import IdentifyBusinessRules
from src.pipelines.project.enrich_business_rules import EnrichBusinessRules
from src.pipelines.project.prepare_vector_store import PrepareVectorStore

class ProjectDiscoveryPipeline(BasePipeline):
    def __init__(self):
        super().__init__()
        self.add_step(LoadFilesV2())
        self.add_step(CheckLanguage())
        self.add_step(LoadProjectV2())
        self.add_step(IdentifyBusinessRules())
        self.add_step(EnrichBusinessRules())
        self.add_step(PrepareVectorStore())

# class ProjectDiscoveryPipeline(BasePipeline):
#     def __init__(self):
#         super().__init__()
#         #self.add_step(LoadFiles()) v1
#         #self.add_step(LoadProject()) v1
#         self.add_step(LoadFilesV2())
#         self.add_step(CheckLanguage())
#         self.add_step(LoadProjectV2())
#         # self.add_step(SearchInProjectContent())
#         # self.add_step(GenerateResponse())