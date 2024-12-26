# src/services/business_rules/analyzer.py
from .analyzers.syntax import BusinessRuleSyntaxAnalyzer
from .analyzers.structure import BusinessRuleStructureAnalyzer
from .analyzers.domain import BusinessRuleDomainAnalyzer

class BusinessRuleAnalyzer:
    def __init__(self):
        self.analyzers = [
            BusinessRuleSyntaxAnalyzer(),
            BusinessRuleStructureAnalyzer(),
            BusinessRuleDomainAnalyzer()
        ]
    
    def analyze_component(self, component):
        all_rules = []
        
        for analyzer in self.analyzers:
            rules = analyzer.analyze(component)
            all_rules.extend(rules)
        
        return self._merge_rules(all_rules)
    
    def _merge_rules(self, rules):
        # Agrupa regras por função
        rules_by_function = {}
        for rule in rules:
            func_name = rule['function_name']
            if func_name not in rules_by_function:
                rules_by_function[func_name] = []
            rules_by_function[func_name].append(rule)
        
        # Merge regras da mesma função
        merged_rules = []
        for func_rules in rules_by_function.values():
            merged = self._merge_function_rules(func_rules)
            merged_rules.append(merged)
        
        return merged_rules
    
    def _merge_function_rules(self, func_rules):
        # Pega a regra com maior confiança como base
        base_rule = max(func_rules, key=lambda r: self._confidence_level(r['confidence']))
        
        # Merge informações adicionais
        for rule in func_rules:
            if rule != base_rule:
                base_rule = self._update_rule_info(base_rule, rule)
        
        return base_rule
    
    def _confidence_level(self, confidence):
        levels = {'high': 3, 'medium': 2, 'low': 1}
        return levels.get(confidence, 0)
    
    def _update_rule_info(self, base_rule, other_rule):
        # Atualiza informações sem sobrescrever as existentes
        if 'domain' not in base_rule and 'domain' in other_rule:
            base_rule['domain'] = other_rule['domain']
        
        if 'domain_attributes' not in base_rule and 'domain_attributes' in other_rule:
            base_rule['domain_attributes'] = other_rule['domain_attributes']
        
        return base_rule