from src.prompts.template import PromptTemplate


class ResponseGenerationPrompt(PromptTemplate):
    _prompt = """
    Gere uma resposta clara e estruturada para uma pergunta sobre regras de negócio, baseada nas regras encontradas no código.

    PERGUNTA ORIGINAL:
    {original_query}

    PERGUNTA EXPANDIDA:
    {expanded_query}

    REGRAS RELEVANTES ENCONTRADAS:
    {relevant_rules}

    FOCO DO DOMÍNIO:
    {domain_focus}

    Forneça uma resposta no seguinte formato:
    {{
        "answer": "Sua resposta detalhada aqui, explicando as regras encontradas e como elas se relacionam",
        "referenced_rules": ["id_regra1", "id_regra2"],
        "suggested_followup": [
            "pergunta sugerida 1?",
            "pergunta sugerida 2?"
        ]
    }}

    DIRETRIZES:
    1. Explique as regras de forma clara e concisa
    2. Conecte regras relacionadas quando relevante
    3. Cite exemplos do código quando útil
    4. Mencione impactos no negócio
    5. Indique dependências importantes
    """

    def __init__(self, query_info: dict, relevant_rules: list):
        rules_text = self._format_rules(relevant_rules)
        domain_focus = ", ".join(query_info["domain_focus"])
        
        default_values = {
            "original_query": query_info["original_query"],
            "expanded_query": query_info["expanded_query"],
            "relevant_rules": rules_text,
            "domain_focus": domain_focus
        }

        super().__init__(
            template=self._prompt,
            input_variables=["original_query", "expanded_query", "relevant_rules", "domain_focus"],
            default_values=default_values
        )

    def _format_rules(self, rules: list) -> str:
        formatted_rules = []
        for rule in rules:
            formatted_rules.append(f"""
            ID: {rule['metadata']['rule_id']}
            Tipo: {rule['metadata']['type']}
            Descrição: {rule['metadata']['description']}
            Impacto: {rule['metadata']['business_impact']}
            Código:
            {rule['content']}
            """)
        return "\n\n".join(formatted_rules)

class QueryExpansionPrompt(PromptTemplate):
    _prompt = """
    Analise a seguinte pergunta sobre regras de negócio em um código e expanda-a para melhorar a busca.

    PERGUNTA ORIGINAL:
    {query}

    CONTEXTO DE DESENVOLVIMENTO:
    Você está analisando código-fonte que contém regras de negócio implementadas.
    Sua tarefa é expandir a pergunta para capturar melhor a intenção e incluir termos relacionados.

    Forneça uma resposta no seguinte formato:
    {{
        "expanded_query": "versão expandida da pergunta",
        "search_terms": ["termo1", "termo2", "termo3"],
        "domain_focus": ["objeto_dominio1", "objeto_dominio2"]
    }}

    EXEMPLOS:

    Pergunta: "Como é calculado o prêmio?"
    Resposta:
    {{
        "expanded_query": "Quais são as regras e fórmulas usadas para calcular o valor do prêmio do seguro",
        "search_terms": ["calculate", "premium", "computation", "formula", "value"],
        "domain_focus": ["premium", "contract", "coverage"]
    }}

    Pergunta: "Quais são as regras do tomador?"
    Resposta:
    {{
        "expanded_query": "Quais são todas as regras de negócio e validações relacionadas ao tomador do seguro",
        "search_terms": ["validate", "check", "verify", "policyholder", "rules"],
        "domain_focus": ["policyholder", "document", "contract"]
    }}
    """

    def __init__(self, query: str):
        super().__init__(
            template=self._prompt,
            input_variables=["query"],
            default_values={"query": query}
        )

class BusinessRuleEnrichmentPrompt(PromptTemplate):
    _prompt = """
    Analise a seguinte regra de negócio encontrada no código e forneça uma análise detalhada.

    REGRA A SER ANALISADA:
    {rules}

    Sua resposta DEVE ser um JSON válido seguindo EXATAMENTE este formato:
    {{
        "analyses": [
            {{
                "rule_id": "ID_DA_REGRA",
                "is_business_rule": true,
                "description": "string descrevendo o que a regra faz",
                "dependencies": ["id_1", "id_2"],
                "rule_type": "validation",
                "domain_objects": ["objeto1", "objeto2"],
                "business_impact": "string descrevendo o impacto",
                "confidence_score": 0.95
            }}
        ]
    }}

    EXEMPLO de resposta esperada:
    {{
        "analyses": [
            {{
                "rule_id": "validateDocument_validation",
                "is_business_rule": true,
                "description": "Valida se um número de documento tem 14 dígitos",
                "dependencies": ["setLastError"],
                "rule_type": "validation",
                "domain_objects": ["document"],
                "business_impact": "Garante que apenas documentos válidos sejam aceitos",
                "confidence_score": 0.95
            }}
        ]
    }}

    IMPORTANTE:
    - SUA RESPOSTA DEVE SER APENAS O JSON, nada mais
    - O campo "analyses" é obrigatório e deve ser uma lista
    - Use o ID exato da regra no campo rule_id
    - Todos os campos são obrigatórios
    - confidence_score deve ser um número entre 0 e 1
    - rule_type deve ser: "validation", "calculation", "process" ou "business_logic"
    """

    def __init__(self, rules):
        rules_text = self._format_rules(rules)
        super().__init__(
            template=self._prompt,
            input_variables=["rules"],
            default_values={"rules": rules_text}
        )

    def _format_rules(self, rules):
        formatted_rules = []
        for rule in rules:
            formatted_rules.append(f"""
            ID da Regra: {rule['id']}
            Nome da Função: {rule['function_name']}
            Tipo Atual: {rule['type']}
            
            Código da Função:
            {rule['content']}
            """)
        return "\n".join(formatted_rules)

# class BusinessRuleEnrichmentPrompt(PromptTemplate):
#     _prompt = """
#     Analise a seguinte regra de negócio encontrada no código e forneça uma descrição.

#     REGRA A SER ANALISADA:
#     {rules}

#     Sua resposta deve ser um JSON no formato:
#     {{
#         "rules": {{
#             "RULE_ID": {{
#                 "description": "descreva o que a regra faz"
#             }}
#         }}
#     }}
#     """

#     def __init__(self, rules):
#         rules_text = self._format_rules(rules)
#         super().__init__(
#             template=self._prompt,
#             input_variables=["rules"],
#             default_values={"rules": rules_text}
#         )

#     def _format_rules(self, rules):
#         formatted_rules = []
#         for rule in rules:
#             formatted_rules.append(f"""
#             ID: {rule['id']}
#             Código:
#             {rule['content']}
#             """)
#         return "\n".join(formatted_rules)
    
# class BusinessRuleEnrichmentPrompt(PromptTemplate):
#     _prompt = """
#     Analise a seguinte regra de negócio encontrada no código e forneça uma análise detalhada no formato JSON especificado.

#     REGRA A SER ANALISADA:
#     {rules}

#     Sua resposta DEVE ser um JSON válido seguindo EXATAMENTE este formato:
#     {{
#         "rules": {{
#             "RULE_ID": {{
#                 "is_business_rule": true,
#                 "description": "string descrevendo o que a regra faz",
#                 "dependencies": ["id_1", "id_2"],
#                 "rule_type": "validation",
#                 "domain_objects": ["objeto1", "objeto2"],
#                 "business_impact": "string descrevendo o impacto",
#                 "confidence_score": 0.95
#             }}
#         }}
#     }}

#     EXEMPLO de resposta esperada:
#     {{
#         "rules": {{
#             "validateDocument_validation": {{
#                 "is_business_rule": true,
#                 "description": "Valida se um número de documento tem 14 dígitos",
#                 "dependencies": ["setLastError"],
#                 "rule_type": "validation",
#                 "domain_objects": ["document"],
#                 "business_impact": "Garante que apenas documentos válidos sejam aceitos",
#                 "confidence_score": 0.95
#             }}
#         }}
#     }}

#     IMPORTANTE:
#     - SUA RESPOSTA DEVE SER APENAS O JSON, nada mais
#     - O campo "rules" é obrigatório e deve ser um objeto
#     - Use o ID exato da regra como chave
#     - Todos os campos são obrigatórios
#     - confidence_score deve ser um número entre 0 e 1
#     - rule_type deve ser: "validation", "calculation", "process" ou "business_logic"
#     """

#     def __init__(self, rules):
#         rules_text = self._format_rules(rules)
#         default_values = {"rules": rules_text}

#         super().__init__(
#             template=self._prompt,
#             input_variables=["rules"],
#             default_values=default_values
#         )

#     def _format_rules(self, rules):
#         formatted_rules = []
#         for rule in rules:
#             formatted_rules.append(f"""
#             ID da Regra: {rule['id']}
#             Nome da Função: {rule['function_name']}
#             Tipo Atual: {rule['type']}
            
#             Código da Função:
#             {rule['content']}
#             """)
#         return "\n".join(formatted_rules)

class DomainRefinementPrompt(PromptTemplate):
    _prompt = """
        Analise os seguintes objetos de domínio e seus atributos encontrados no código:
        
        {domains}
        
        Por favor:
        1. Identifique quais são realmente objetos de domínio do negócio
        2. Sugira atributos adicionais comuns para cada domínio
        3. Identifique relacionamentos entre os domínios
        4. Remova falsos positivos
        """

    def __init__(self, domains):
        default_values = {"domains": domains}

        super().__init__(
            template=self._prompt,
            input_variables=["domains"],
            default_values=default_values
        )

class BusinessAnalystPrompt(PromptTemplate):
    _prompt = """
    Você é um analista de negócios experiente em projetos de desenvolvimento de software, apoiando o entendimento de projetos e levantamento de requisitos funcionais para diferentes negócios.
    Sua tarefa responder a questões enviadas pelo usuário utilizando a documentação de referência para isso.
    Mantenha o nome de arquivos, classes, propriedades e atributos no mesmo idioma que estiver no arquivo, mas elabore o texto da resposta sempre em português brasileiro.

    Documentação de referência
    {knowledge_base}
    """

    def __init__(self, knowledge_base):

        default_values = {"knowledge_base": knowledge_base}
        super().__init__(
            template=self._prompt,
            input_variables=["knowledge_base"],
            default_values=default_values
        )


class CPlusPlusInfoPrompt(PromptTemplate):
    _prompt = """
    Você um experiente engenheiro de software C++ com profundo conhecimento e experiência tabalhando em projetos legados escritos com C++.
    Sua tarefa é analisar códigos em C++ para identificar regras de negócio, entidades e também dependências
    Mantenha o nome de arquivos, classes, propriedades e atributos no mesmo idioma que estiver no arquivo, mas elabore o texto da resposta sempre em português brasileiro.
    """

    def __init__(self):
        super().__init__(
            template=self._prompt,
            input_variables=[]
        )


class RolePrompt(PromptTemplate):
    _prompt = """
    Você é um assistente de atendimento ao cliente prestativo que pode classificar um topico recebido em alguma das categorias e criar uma resposta.
    
    Aqui estão as diretrizes gerais:
    - Quando o topico for sobre discovery de projeto ou código legado for mencionado, classifique como project-discovery
    - Quando o tópico estiver relacionado à arquitetura de software, classifique como general
    - Quando não for possível classificar como project-discovery ou general, classifique como other
    """ 

    def __init__(self, topic):

        default_values = {"topic": topic} 

        super().__init__(
            template=self._prompt,
            input_variables=[]
            #default_values=default_values
        )


# class RolePrompt(PromptTemplate):
#     def __init__(self):
#         default_values = {"name": "Anna", "company": "Datalumina"}
#         super().__init__(
#             template=prompt,
#             input_variables=["name", "company"],
#             default_values=default_values
#         )

# prompt = """
# You're an assistant name {name}, working for {company}.
# You're goal is help process incoming tickets and generate responses.

# Here's are general guidelines:
# - We currenly don't do any collcaborations. When a collaboration is mentioned, response with a pol
# - Always sign off with your name and company name using `King regard`.
# """
