import sys
import time
import random
from typing import Callable, Optional

class LLMStyleConsole:
    def __init__(self, 
                 min_delay: float = 0.01, 
                 max_delay: float = 0.03, 
                 end_delay: float = 0.5,
                 callback: Optional[Callable[[str], None]] = None):
        """
        Inicializa a classe LLMStyleConsole.
        
        Args:
            min_delay: Delay mínimo entre caracteres (segundos)
            max_delay: Delay máximo entre caracteres (segundos)
            end_delay: Delay após completar uma frase (segundos)
            callback: Função opcional para processar a resposta do usuário
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.end_delay = end_delay
        self.callback = callback

    def _type_text(self, text: str) -> None:
        """
        Exibe o texto caractere por caractere com delays aleatórios.
        """
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            
            # Delay maior para pontuação para efeito mais natural
            if char in '.!?':
                time.sleep(self.max_delay * 2)
            else:
                time.sleep(random.uniform(self.min_delay, self.max_delay))
        
        # Delay final após completar o texto
        time.sleep(self.end_delay)
        print()  # Nova linha após o texto

    def get_response(self, prompt: str = "") -> str:
        """
        Obtém a resposta do usuário.
        
        Args:
            prompt: Texto opcional para prefixar o input
        
        Returns:
            str: Resposta do usuário
        """
        return input(prompt)

    def display_and_get_response(self, text: str, input_prompt: str = "> ", callback: Optional[Callable[[str], None]] = None) -> str:
        """
        Exibe o texto no estilo LLM e obtém a resposta do usuário.
        
        Args:
            text: Texto a ser exibido
            input_prompt: Prompt para a entrada do usuário
            
        Returns:
            str: Resposta do usuário
        """

        if(callback):
            self.callback = callback
        
        self._type_text(text)
        response = self.get_response(input_prompt)
        
        if self.callback:
            self.callback(response)
            
        return response