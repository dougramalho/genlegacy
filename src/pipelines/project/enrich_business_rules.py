# src/pipelines/steps/enrich_business_rules.py
from src.pipelines.base import PipelineStep
from src.api.models import BaseTaskInput, ProcessingContext, OutputDataModel, BusinessRulesAnalysis
from src.services.llm_factory import LLMFactory
from src.prompts.role import BusinessRuleEnrichmentPrompt
import json

class EnrichBusinessRules(PipelineStep):
    def __init__(self):
        self.llm_client = LLMFactory("openai")
    
    def process(self, 
                input_data: BaseTaskInput, 
                context: ProcessingContext, 
                output_data=OutputDataModel):
        
        rules = context.intermediates.get("initial_business_rules", [])
        uncertain_rules = [r for r in rules if r['confidence'] != 'high']
        
        if uncertain_rules:
            enriched_rules = self._enrich_rules(uncertain_rules)
            self._update_rules(rules, enriched_rules)
        
        context.intermediates["enriched_business_rules"] = rules
        return input_data, context, output_data
    
    # def _enrich_rules(self, uncertain_rules):
    #     try:
    #         prompt = BusinessRuleEnrichmentPrompt(uncertain_rules[:1])
            
    #         completion = self.llm_client.create_completion(
    #             response_model=BusinessRulesAnalysis,
    #             temperature=0,
    #             messages=[
    #                 {
    #                     "role": "user",
    #                     "content": prompt.format()
    #                 }
    #             ]
    #         )

    #         return self._process_llm_response(uncertain_rules, completion)
    #     except Exception as e:
    #         print(f"Error during LLM completion: {str(e)}")
    #         return uncertain_rules
    def _enrich_rules(self, uncertain_rules):
        try:
            prompt = BusinessRuleEnrichmentPrompt(uncertain_rules)
            
            # Para debug
            print("Prompt enviado:")
            print(prompt.format())

            completion = self.llm_client.create_completion(
                response_model=BusinessRulesAnalysis,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt.format()
                    }
                ]
            )

            # Para debug mais detalhado
            print("\nResposta do LLM (raw):")
            print(completion)
            
            print("\nTipo da resposta:")
            print(type(completion))
            
            print("\nAtributos da resposta:")
            print(dir(completion))

            return self._process_llm_response(uncertain_rules, completion)
        except Exception as e:
            print(f"Error during LLM completion: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error args: {e.args}")
            return uncertain_rules
    
    def _process_llm_response(self, original_rules, enriched_analysis: BusinessRulesAnalysis):
        """
        Processa a resposta do LLM e atualiza as regras originais
        """
        enriched_rules = []
        
        # Cria um dicionário para facilitar o lookup
        analysis_by_id = {
            analysis.rule_id: analysis 
            for analysis in enriched_analysis.analyses
        }
        
        for rule in original_rules:
            rule_id = rule['id']
            if rule_id in analysis_by_id:
                analysis = analysis_by_id[rule_id]
                
                if analysis.is_business_rule:
                    rule.update({
                        'confidence': 'high' if analysis.confidence_score > 0.7 else 'medium',
                        'description': analysis.description,
                        'dependencies': analysis.dependencies,
                        'type': analysis.rule_type,
                        'domain_objects': analysis.domain_objects,
                        'business_impact': analysis.business_impact,
                        'confidence_score': analysis.confidence_score
                    })
                else:
                    rule['confidence'] = 'low'
                
                enriched_rules.append(rule)
            else:
                enriched_rules.append(rule)
                
        return enriched_rules

    def _update_rules(self, original_rules, enriched_rules):
        """
        Atualiza as regras originais com as informações enriquecidas
        """
        enriched_dict = {rule['id']: rule for rule in enriched_rules}
        for i, rule in enumerate(original_rules):
            if rule['id'] in enriched_dict:
                original_rules[i] = enriched_dict[rule['id']]