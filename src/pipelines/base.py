from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel


class PipelineStep(ABC):
    @abstractmethod
    def process(
        self,
        data: BaseTaskInput,
        context: ProcessingContext,
        output_data: OutputDataModel,
    ) -> Tuple[BaseTaskInput, ProcessingContext, OutputDataModel]:
        pass

class BasePipeline(ABC):
    def __init__(self):
        self.steps: List[PipelineStep] = []
        self.parameters: Dict = {}

    def add_step(self, step: PipelineStep):
        self.steps.append(step)

    def run(
        self, input_data: BaseTaskInput
    ) -> Tuple[ProcessingContext, OutputDataModel]:
        context = ProcessingContext()
        output_data = OutputDataModel()

        for step in self.steps:
            input_data, context, output_data = step.process(
                input_data, context, output_data
            )
        
        return context, output_data