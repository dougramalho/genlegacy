from src.pipelines.orchestration.welcome_user import WelcomeUser
from src.pipelines.orchestration.categorize_subject import CategorizeSubject


from src.pipelines.base import BasePipeline

class InitializeSessionPipeline(BasePipeline):
    def __init__(self):
        super().__init__()
        self.add_step(WelcomeUser())
        self.add_step(CategorizeSubject())