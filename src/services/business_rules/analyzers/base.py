from abc import ABC, abstractmethod

class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, component):
        pass

    def create_rule(self, function, rule_type, confidence, source):
        return {
            'id': f"{function['name']}_{rule_type}",
            'function_name': function['name'],
            'return_type': function['return_type'],
            'content': function['content'],
            'type': rule_type,
            'confidence': confidence,
            'source': source
        }