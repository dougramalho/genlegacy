from .base import BaseAnalyzer
from .domain_discovery import DomainObjectDiscovery
from src.services.llm_factory import LLMFactory
from src.prompts.role import DomainRefinementPrompt
from src.api.models import Reply


class BusinessRuleDomainAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.domain_discovery = DomainObjectDiscovery()
        self.llm_client = LLMFactory("openai")
        self.domain_objects = None  # Será preenchido durante a análise
    
    def prepare(self, component):
        """
        Prepara o analisador descobrindo os objetos de domínio
        """
        # Primeira etapa: Descoberta estática
        potential_domains = self.domain_discovery.discover_from_components([component])
        
        # Segunda etapa: Refinamento com LLM
        self.domain_objects = self._refine_with_llm(potential_domains)
    
    def _refine_with_llm(self, potential_domains):
        """
        Usa LLM para refinar a descoberta de domínios
        """
        prompt = DomainRefinementPrompt(potential_domains)

        completion = self.llm_client.create_completion(
            response_model=None,
            temperature=0,
            messages=[
                {
                    "role":"user",
                    "content": prompt.format()
                }
            ]
        )
        
        return potential_domains
    
    def _create_domain_refinement_prompt(self, potential_domains):
        prompt = """
        Analise os seguintes objetos de domínio e seus atributos encontrados no código:
        
        {domains}
        
        Por favor:
        1. Identifique quais são realmente objetos de domínio do negócio
        2. Sugira atributos adicionais comuns para cada domínio
        3. Identifique relacionamentos entre os domínios
        4. Remova falsos positivos
        """
        
        domains_text = "\n".join(
            f"- {domain}:\n  Atributos: {', '.join(attrs)}"
            for domain, attrs in potential_domains.items()
        )
        
        return prompt.format(domains=domains_text)

    def _is_domain_related(self, content, domain, attributes):
        return (
            domain in content and
            any(attr in content for attr in attributes)
        )
    
    def _find_related_attributes(self, content, attributes):
        return [attr for attr in attributes if attr in content]
    
    def analyze(self, component):
        # Garante que temos os objetos de domínio descobertos

        if self.domain_objects is None:
            self.prepare(component)

        if self.domain_objects is None:
            raise ValueError("Analyzer not prepared. Call prepare() first.")
            
        rules = []
        for function in component['functions']:
            content = function['content'].lower()
            
            for domain, attributes in self.domain_objects.items():
                if self._is_domain_related(content, domain, attributes):
                    rule = self.create_rule(
                        function=function,
                        rule_type='domain_rule',
                        confidence='medium',
                        source='domain_analysis'
                    )
                    rule['domain'] = domain
                    rule['domain_attributes'] = self._find_related_attributes(content, attributes)
                    rules.append(rule)
        
        return rules