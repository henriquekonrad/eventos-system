# utils/validators.py
"""
Validadores de dados.
Centraliza lógica de validação para reuso.
"""
import re
from typing import Tuple

class Validators:
    """
    Classe com métodos estáticos para validação.
    Padrão: Utility Class (apenas métodos estáticos)
    """
    
    @staticmethod
    def validar_cpf(cpf: str) -> Tuple[bool, str]:
        """
        Valida CPF brasileiro, simplificado
        
        Returns:
            (valido: bool, mensagem: str)
        """
        cpf_numeros = re.sub(r'\D', '', cpf)
        
        # Para ser simplificado, utilizei somente validação de tamanho
        if len(cpf_numeros) != 11:
            return False
        
        return True
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, str]:
        """
        Valida formato de email.
        
        Returns:
            (valido: bool, mensagem: str)
        """
        # Padrão básico de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not email:
            return False
        
        if not re.match(pattern, email):
            return False
        
        return True
    
    @staticmethod
    def validar_nome(nome: str, min_length: int = 3) -> Tuple[bool, str]:
        """
        Valida nome de pessoa.
        
        Args:
            nome: Nome a validar
            min_length: Tamanho mínimo
            
        Returns:
            (valido: bool, mensagem: str)
        """
        if not nome or not nome.strip():
            return False
        
        if len(nome.strip()) < min_length:
            return False
        
        # Verifica se tem pelo menos um espaço (nome + sobrenome)
        if ' ' not in nome.strip():
            return False
        
        return True


# Exemplo de uso:
if __name__ == "__main__":
    # Testes
    print(Validators.validar_cpf("123.456.789-09"))
    print(Validators.validar_email("teste@email.com"))
    print(Validators.validar_nome("João Silva"))