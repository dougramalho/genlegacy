# src/services/project_loader/cpp_loader.py
from typing import Dict, Any, List, Set
from pathlib import Path
import os
import re
from .base import BaseProjectLoader

class CppComponent:
    def __init__(self, path: Path):
        self.path = path
        self.type = 'header' if path.suffix in ['.h', '.hpp'] else 'source'
        self.includes: Set[str] = set()
        self.namespaces: Set[str] = set()
        self.classes: List[Dict] = []
        self.functions: List[Dict] = []
        self.templates: List[Dict] = []
        self.operators: List[Dict] = []
        self.dependencies: Set[str] = set()
        self.used_by: Set[str] = set()

class CppProjectLoader(BaseProjectLoader):
    def __init__(self):
        self.components: Dict[str, CppComponent] = {}
        self._template_pattern = re.compile(r'template\s*<[^>]+>\s*(class|struct|typename)\s+(\w+)')
        self._operator_pattern = re.compile(r'operator\s*([+\-*/=%^&|<>!]+|\[\]|\(\))\s*\([^)]*\)')
        self._class_pattern = re.compile(r'class\s+(\w+)(?:\s*:\s*(?:public|private|protected)\s+(\w+))?')
        self._function_pattern = re.compile(r'(?:virtual\s+)?(?:static\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\([^)]*\)')

        # self._function_pattern = re.compile(
        #     r'(?:^|;|\})\s*'                           # Início de declaração 
        #     r'(?:virtual\s+)?'                         # Modificador virtual
        #     r'(?:static\s+)?'                          # Modificador static
        #     r'(?:inline\s+)?'                          # Modificador inline
        #     r'(?:explicit\s+)?'                        # Modificador explicit
        #     r'(?:const\s+)?'                           # Modificador const
        #     r'(?!if|else|for|while|switch|return)'     # Negative lookahead para palavras reservadas
        #     r'(\w+(?:\s*[*&])?(?:<[^>]+>)?)'          # Tipo de retorno com possíveis ponteiros/referencias
        #     r'\s+'                                     # Espaço obrigatório
        #     r'(\w+)'                                   # Nome da função
        #     r'\s*\([^)]*\)'                           # Parâmetros
        #     r'(?:\s*const)?'                          # Possível const após parâmetros
        #     r'(?=\s*{|\s*;)'                          # Seguido por { ou ;
        # )

        self._function_pattern = re.compile(
            r'(?:^|;|\})\s*'                           # Início de declaração 
            r'(?:virtual\s+)?'                         # Modificador virtual
            r'(?:static\s+)?'                          # Modificador static
            r'(?:inline\s+)?'                          # Modificador inline
            r'(?:explicit\s+)?'                        # Modificador explicit
            r'(?:const\s+)?'                           # Modificador const
            r'(?!if|else|for|while|switch|return)'     # Negative lookahead para palavras reservadas
            r'(\w+(?:\s*[*&])?(?:<[^>]+>)?)'          # Tipo de retorno com possíveis ponteiros/referencias
            r'\s+'                                     # Espaço obrigatório
            r'(\w+)'                                   # Nome da função
            r'\s*\([^)]*\)'                           # Parâmetros
            r'(?:\s*const)?'                          # Possível const após parâmetros
            r'(?=\s*{)'                               # Seguido por { (removemos ;)
        )

        self._cpp_keywords = {
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 
            'continue', 'return', 'try', 'catch', 'throw', 'goto'
        }
        

    def load(self, project_path: str) -> Dict[str, Any]:
        # Primeira passagem: Coleta informações básicas
        self._collect_components(project_path)
        
        # Segunda passagem: Análise de dependências
        self._analyze_dependencies()
        
        return self._build_project_info()

    def _collect_components(self, project_path: str):
        for root, _, files in os.walk(project_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in ['.cpp', '.hpp', '.h', '.cc']:
                    component = CppComponent(file_path)
                    self._analyze_file(component)
                    self.components[str(file_path)] = component

    def _extract_function_body(self, content: str, start_pos: int) -> str:
        """
        Extrai o corpo completo da função incluindo a declaração
        """
        try:
            # Encontra a primeira chave de abertura
            pos = start_pos
            while pos < len(content) and content[pos] != '{':
                pos += 1
            
            if pos >= len(content):
                return ""

            # Conta chaves para encontrar o fechamento correto
            count = 1
            pos += 1  # Pula a primeira chave
            
            # Captura o conteúdo completo da função
            declaration = content[start_pos:pos].strip()
            body_start = pos
            
            while count > 0 and pos < len(content):
                if content[pos] == '{':
                    count += 1
                elif content[pos] == '}':
                    count -= 1
                pos += 1

            if count == 0:
                body = content[body_start:pos-1]  # -1 para não incluir a última chave
                return f"{declaration}{{\n{body}}}"
                
            return ""
            
        except Exception as e:
            print(f"Error extracting function body: {str(e)}")
            return ""
    
    def _analyze_file(self, component: CppComponent):
        try:
            with open(component.path, 'r', encoding='utf-8') as f:
                content = f.read()

                # Análise de includes
                includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', content)
                component.includes.update(includes)
                
                # Análise de namespaces
                namespaces = re.findall(r'namespace\s+(\w+)', content)
                component.namespaces.update(namespaces)
                
                # Análise de templates
                for match in self._template_pattern.finditer(content):
                    component.templates.append({
                        'type': match.group(1),
                        'name': match.group(2),
                        'line': content[:match.start()].count('\n') + 1
                    })
                
                # Análise de operadores sobrecarregados
                for match in self._operator_pattern.finditer(content):
                    component.operators.append({
                        'operator': match.group(1),
                        'line': content[:match.start()].count('\n') + 1
                    })
                
                # Análise de classes e heranças
                for match in self._class_pattern.finditer(content):
                    class_info = {
                        'name': match.group(1),
                        'base_class': match.group(2) if match.group(2) else None,
                        'line': content[:match.start()].count('\n') + 1
                    }
                    component.classes.append(class_info)
                
                # Análise de funções
                for match in self._function_pattern.finditer(content):
                    component.functions.append({
                        'return_type': match.group(1),
                        'name': match.group(2),
                        'line': content[:match.start()].count('\n') + 1
                    })

                functions_dict  = {}

                # Análise de funções com filtro de palavras reservadas
                for match in self._function_pattern.finditer(content):
                    return_type = match.group(1).strip()
                    function_name = match.group(2).strip()
                    
                    if (not function_name.startswith(('if', 'else', 'for', 'while', 'switch', 'return')) and
                        not return_type.startswith(('if', 'else', 'for', 'while', 'switch', 'return'))):
                        
                        # Extrair o corpo da função
                        function_content = self._extract_function_body(content, match.start())
                        
                        # Usar função_name como chave para evitar duplicatas
                        if function_name not in functions_dict or function_content:
                            functions_dict[function_name] = {
                                'return_type': return_type,
                                'name': function_name,
                                'line': content[:match.start()].count('\n') + 1,
                                'content': function_content
                            }

                # Converter o dict para lista no final
                component.functions = list(functions_dict.values())

        except Exception as e:
            print(f"Error analyzing file {component.path}: {str(e)}")

    def _analyze_dependencies(self):
        """
        Analisa dependências entre componentes baseado em includes e uso de classes
        """
        for comp_path, component in self.components.items():
            # Mapeia includes para componentes reais do projeto
            for include in component.includes:
                include_path = self._resolve_include_path(include, component.path)
                if include_path in self.components:
                    component.dependencies.add(include_path)
                    self.components[include_path].used_by.add(comp_path)

    def _resolve_include_path(self, include: str, current_file: Path) -> str:
        """
        Tenta resolver o caminho real de um arquivo incluído
        """
        # Remove extensão se presente no include
        include_base = Path(include).stem
        
        # Procura por arquivos que correspondam ao include
        for comp_path in self.components:
            if Path(comp_path).stem == include_base:
                return comp_path
        return include

    def _build_project_info(self) -> Dict[str, Any]:
        return {
            'components': [
                {
                    'path': str(comp.path),
                    'type': comp.type,
                    'includes': list(comp.includes),
                    'namespaces': list(comp.namespaces),
                    'classes': comp.classes,
                    'functions': comp.functions,
                    'templates': comp.templates,
                    'operators': comp.operators,
                    'dependencies': list(comp.dependencies),
                    'used_by': list(comp.used_by)
                }
                for comp in self.components.values()
            ],
            'dependencies_graph': self._build_dependencies_graph(),
            'build_system': self._detect_build_system(),
            'metrics': self._calculate_metrics()
        }

    def _build_dependencies_graph(self) -> Dict[str, List[str]]:
        """
        Cria um grafo de dependências entre componentes
        """
        return {
            str(comp_path): list(component.dependencies)
            for comp_path, component in self.components.items()
        }

    def _detect_build_system(self) -> str:
        # Implementação atual mantida...
        pass

    def _calculate_metrics(self) -> Dict[str, Any]:
        """
        Calcula métricas do projeto
        """
        return {
            'total_components': len(self.components),
            'total_classes': sum(len(c.classes) for c in self.components.values()),
            'total_functions': sum(len(c.functions) for c in self.components.values()),
            'total_templates': sum(len(c.templates) for c in self.components.values()),
            'total_operators': sum(len(c.operators) for c in self.components.values()),
        }