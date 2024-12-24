from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel
from pydantic import BaseModel
from typing import List, Dict
import os
from pathlib import Path
from src.services.language_detection import LanguageDetectionStrategy, ResponseCheckLanguageModel
from src.utils import LLMStyleConsole

class CheckLanguage(PipelineStep):
    def __init__(self):
        self.detector = LanguageDetectionStrategy()

    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        completion = self.check_language(context.intermediates["project_path"])

        context.intermediates["language"] = completion.language
        context.intermediates["language_confidence"] = completion.confidence
        context.intermediates["detected_files"] = completion.detected_files
        context.intermediates["main_files"] = completion.main_files

        console = LLMStyleConsole()

        welcome_text = f"Identifiquei que trata-se de um projeto em {completion.language}"

        console._type_text(welcome_text)

        return input_data, context, output_data
    
    def check_language(self, project_path: str) -> ResponseCheckLanguageModel:
        return self.detector.detect(project_path)