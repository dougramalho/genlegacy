from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel
from src.services.business_rules.analyzer import BusinessRuleAnalyzer

class IdentifyBusinessRules(PipelineStep):
    def __init__(self):
        self.rule_analyzer = BusinessRuleAnalyzer()
    
    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        components = context.intermediates.get("components", [])
        business_rules = []
        
        for component in components:
            rules = self.rule_analyzer.analyze_component(component)
            business_rules.extend(rules)
        
        context.intermediates["initial_business_rules"] = business_rules
        return input_data, context, output_data