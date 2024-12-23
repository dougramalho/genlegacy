from src.pipelines.project.check_language import CheckLanguage
from src.pipelines.project.load_files import LoadFiles
from src.pipelines.project.generate_response import GenerateResponse
from src.pipelines.base import BasePipeline
from src.pipelines.project.load_project_pipeline import LoadProject
from src.pipelines.project.search_project import SearchInProjectContent

class ProjectDiscoveryPipeline(BasePipeline):
    def __init__(self):
        super().__init__()
        self.add_step(LoadFiles())
        self.add_step(CheckLanguage())
        self.add_step(LoadProject())
        self.add_step(SearchInProjectContent())
        self.add_step(GenerateResponse())