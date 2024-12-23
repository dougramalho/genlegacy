from typing import Dict, List, Optional
from string import Formatter

class PromptTemplate:
    def __init__(
        self,
        template: str,
        input_variables: List[str],
        default_values: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a PromptTemplate.
        
        Args:
            template (str): The prompt template with variables in {variable} format
            input_variables (List[str]): List of variable names used in the template
            default_values (Dict[str, str], optional): Default values for variables
        """
        self.template = template
        self.input_variables = input_variables
        self.default_values = default_values or {}
        
        # Validate template variables against input_variables
        self._validate_template()
    
    def _validate_template(self) -> None:
        """Validate that all template variables are accounted for."""
        # Extract all variables from template using string.Formatter
        template_variables = {
            name for _, name, _, _ in Formatter().parse(self.template) 
            if name is not None
        }
        
        # Check if all template variables are in input_variables
        missing_vars = template_variables - set(self.input_variables)
        if missing_vars:
            raise ValueError(
                f"Template has variables {missing_vars} that are not in input_variables"
            )
    
    def format(self, **kwargs: Dict[str, str]) -> str:
        """
        Format the prompt template with provided variables.
        
        Args:
            **kwargs: Variable values to format the template with
            
        Returns:
            str: The formatted prompt
        
        Raises:
            ValueError: If required variables are missing
        """
        # Merge default values with provided values
        variables = {**self.default_values, **kwargs}
        
        # Check for missing variables
        missing_vars = set(self.input_variables) - set(variables.keys())
        if missing_vars:
            raise ValueError(
                f"Missing values for variables: {missing_vars}"
            )
        
        return self.template.format(**variables)
    
    def get_variables(self) -> List[str]:
        """Return list of all variables in the template."""
        return self.input_variables
    
    def get_default_values(self) -> Dict[str, str]:
        """Return dictionary of default values."""
        return self.default_values.copy()
    
    def partial(self, **kwargs: Dict[str, str]) -> "PromptTemplate":
        """
        Create a new PromptTemplate with some variables pre-filled.
        
        Args:
            **kwargs: Variables to pre-fill
            
        Returns:
            PromptTemplate: A new template with updated default values
        """
        new_defaults = {**self.default_values, **kwargs}
        return PromptTemplate(
            template=self.template,
            input_variables=self.input_variables,
            default_values=new_defaults
        )