from .base import BaseAnalyzer

class BusinessRuleSyntaxAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.rule_prefixes = ['validate', 'check', 'calculate', 'process', 'verify', 'validar', 'calcular']
        self.rule_suffixes = ['Rule', 'Policy', 'Validation']

    def analyze(self, component):
        rules = []
        for function in component['functions']:
            if self._is_business_rule(function['name']):
                rule = self.create_rule(
                    function=function,
                    rule_type='business_rule',
                    confidence='high',
                    source='name_pattern'
                )
                rules.append(rule)
        return rules
    
    def _is_business_rule(self, function_name):
        name = function_name.lower()
        return (
            any(name.startswith(prefix.lower()) for prefix in self.rule_prefixes) or
            any(name.endswith(suffix.lower()) for suffix in self.rule_suffixes)
        )