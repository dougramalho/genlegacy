from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel
from pydantic import BaseModel, BeforeValidator
import instructor
from openai import OpenAI
from src.api.models import Reply, ProcessCategory
from typing_extensions import Annotated
from instructor import llm_validator
from src.services.llm_factory import LLMFactory
from src.prompts.role import RolePrompt

client = instructor.from_openai(OpenAI())


class ResponseTopicModel(BaseModel):
    category: ProcessCategory = None

    def __init__(self, category: ProcessCategory):
        super().__init__()
        self.category = category

class ValidateReply(BaseModel):
    content: Annotated[
        str,
        BeforeValidator(
            llm_validator(
                statement="Never say things that could hurt the reputation of the company",
                client=client,
                allow_override=True
            )
        )
    ]

class CategorizeSubject(PipelineStep):

    def __init__(self):
        super().__init__()
        self.topic = None
        self.message = None

    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        self.message = context.intermediates["message"]
        completion = self.categorize_subject(input_data)

        context.intermediates["topic"] = completion.category

        output_data.result["category"] = completion.category
        output_data.metadata["categorization_source"] = "llm"
        output_data.result["message"] = context.intermediates["message"]

        return input_data, context, output_data
    
    def categorize_subject(self, data: BaseTaskInput) -> ResponseTopicModel:
        
        llm = LLMFactory("openai")
        prompt = RolePrompt(self.message)

        completion = llm.create_completion(
            response_model=Reply,
            temperature=0,
            messages=[
                {
                    "role":"system",
                    "content": prompt.format()
                },
                {
                    "role":"user",
                    "content": f"O tópico que precisamos classificar é: {self.message}"
                }
            ]
        )

        # reply = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     response_model=Reply,
        #     max_retries=3, #default value
        #     messages=[
        #         {
        #             "role":"system",
        #             "content":"You're a helpful customer care assistant that can clasiffy incoming messages and create a response."
        #         },
        #         {
        #             "role":"user",
        #             "content": self.topic
        #         }
        #     ]
        # )


        
        
        data = ResponseTopicModel(completion.category)
        return data