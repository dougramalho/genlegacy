from typing import Dict, Set, List
import re

class DomainObjectDiscovery:
    def __init__(self):
        self.potential_domains: Dict[str, Set[str]] = {}
        
    def discover_from_components(self, components: List[dict]) -> Dict[str, Set[str]]:
        """Descobre objetos de domínio analisando o código"""
        
        for component in components:
        # Verifica se o componente é um dicionário
            if not isinstance(component, dict):
                print(f"Warning: Invalid component format: {component}")
                continue
                
            # Primeira passagem: encontra estruturas de dados/classes
            self._find_data_structures(component)
            
            # Segunda passagem: analisa uso em funções
            self._analyze_function_usage(component)
        
        # Terceira passagem: relaciona atributos
        self._correlate_attributes()
        
        return self.potential_domains

    def _find_data_structures(self, component: dict):
        """
        Identifica estruturas que parecem ser objetos de domínio
        olhando para classes, structs, e tipos
        """

        # Verifica se há includes
        includes = component.get('includes', [])
        for include in includes:
            if isinstance(include, str) and include.endswith('.h'):
                self._analyze_header_file(include)

        # Analisa funções
        functions = component.get('functions', [])
        for function in functions:
            if isinstance(function, dict):
                content = function.get('content', '')
                self._extract_types_from_content(content)

    def _analyze_header_file(self, header_path: str):
        """Analisa arquivo de header para encontrar definições de tipos"""
        try:
            # Aqui você implementaria a lógica para ler e analisar o arquivo .h
            # Por enquanto, vamos apenas registrar para implementação futura
            pass
        except Exception as e:
            print(f"Error analyzing header file {header_path}: {str(e)}")

    def _extract_types_from_content(self, content: str):
        """Extrai tipos e seus atributos do conteúdo"""
        # Procura por declarações de classe/struct
        class_pattern = r'(?:class|struct)\s+(\w+)'
        classes = re.finditer(class_pattern, content)
        
        for match in classes:
            class_name = match.group(1)
            # Ignora nomes muito genéricos
            if not self._is_generic_name(class_name):
                self.potential_domains[class_name] = set()

    def _analyze_function_usage(self, component: dict):
        """Analisa como as funções usam e manipulam objetos"""
        functions = component.get('functions', [])
        for function in functions:
            if isinstance(function, dict):
                content = function.get('content', '').lower()
                
                # Analisa parâmetros da função
                if 'const' in content and '&' in content:
                    self._extract_parameter_types(content)
                
                # Analisa uso de membros/atributos
                for domain in self.potential_domains:
                    if domain.lower() in content:
                        self._extract_attributes(domain, content)


    def _extract_parameter_types(self, content: str):
        """Extrai tipos dos parâmetros das funções"""
        param_pattern = r'(?:const\s+)?(\w+)(?:\s*[&*])?\s+(\w+)'
        for match in re.finditer(param_pattern, content):
            type_name, var_name = match.groups()
            if not self._is_generic_name(type_name):
                self.potential_domains.setdefault(type_name, set())

    def _extract_attributes(self, domain: str, content: str):
        """Extrai atributos baseado no uso"""
        # Procura por acessos a membros (-> ou .)
        member_pattern = f"{domain.lower()}\\w*[->.]([a-zA-Z]\\w*)"
        matches = re.finditer(member_pattern, content)
        
        for match in matches:
            attribute = match.group(1)
            if not self._is_generic_name(attribute):
                self.potential_domains[domain].add(attribute)

    def _correlate_attributes(self):
        """
        Correlaciona atributos entre domínios para identificar relacionamentos
        e remover falsos positivos
        """
        # Remove domínios com muito poucos atributos
        self.potential_domains = {
            domain: attrs 
            for domain, attrs in self.potential_domains.items() 
            if len(attrs) >= 2  # Mínimo de atributos para considerar um domínio válido
        }

    def _is_generic_name(self, name: str) -> bool:
        """Verifica se um nome é muito genérico para ser um objeto de domínio"""
        generic_names = {
            'string', 'int', 'bool', 'void', 'char', 'double', 'float',
            'data', 'info', 'details', 'result', 'value', 'item', 'node'
        }
        return name.lower() in generic_names