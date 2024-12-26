from .base import BaseAnalyzer

class BusinessRuleStructureAnalyzer(BaseAnalyzer):

    def analyze(self, component):
        rules = []
        for function in component['functions']:
            content = function['content'].lower()
            
            # Verifica padrões estruturais
            if self._has_validation_pattern(content):
                rule = self.create_rule(
                    function=function,
                    rule_type='validation_rule',
                    confidence='medium',
                    source='error_handling'
                )
                rules.append(rule)
                
            elif self._has_calculation_pattern(content):
                rule = self.create_rule(
                    function=function,
                    rule_type='calculation_rule',
                    confidence='medium',
                    source='calculation_pattern'
                )
                rules.append(rule)
        
        return rules
    
    def _has_validation_pattern(self, content):
        validation_indicators = [
            'return false',
            'seterror',
            'throw',
            'invalid',
            'validate'
        ]
        return any(indicator in content for indicator in validation_indicators)
    
    def _has_calculation_pattern(self, content):
        calculation_indicators = [
            'calculate',
            'compute',
            'sum',
            'total',
            'average'
        ]
        return any(indicator in content for indicator in calculation_indicators)