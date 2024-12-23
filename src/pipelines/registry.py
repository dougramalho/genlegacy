from src.pipelines.project.project_discovery_pipeline import ProjectDiscoveryPipeline
from src.pipelines.orchestration.manager_classifier_pipeline import InitializeSessionPipeline
from src.api.models import WelcomeTaskInput, DiscoveryTaskInput, BaseTaskInput

class PipelineRegistry:

    _pipeline_mapping = {
        WelcomeTaskInput: InitializeSessionPipeline,
        DiscoveryTaskInput: ProjectDiscoveryPipeline
    }

    @classmethod  # Mudando para @classmethod
    def get_pipeline(cls, input_data: BaseTaskInput):
        pipeline_class = cls._pipeline_mapping.get(type(input_data))

        if pipeline_class is None:
            raise ValueError(f"Unknown task type: {type(input_data)}")
            
        return pipeline_class()