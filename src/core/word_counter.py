"""
WordCounter: conteo determinístico de palabras.
Proporciona una forma consistente de contar palabras en un texto.
"""

import re
from typing import List


class WordCounter:
    """
    Contador de palabras con estrategia consistente.
    Estrategia: separación por espacios, manejo de puntuación.
    """

    # Patrones para tokens críticos (se preservan exactamente)
    CRITICAL_TOKENS_PATTERNS = [
        r'\d+[.,]\d+',  # Números decimales (1.5, 3,14)
        r'\d+\s*%',      # Porcentajes (25%, 50 %)
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # Fechas (01/02/2024)
        r'\b[A-Z]{2,}\b',  # Acrónimos (USA, ONU)
    ]

    def __init__(self, strategy: str = "whitespace"):
        """
        Inicializa el contador.
        
        Args:
            strategy: "whitespace" (por defecto) separa por espacios.
        """
        self.strategy = strategy

    def count(self, text: str) -> int:
        """
        Cuenta palabras en el texto.
        
        Definición: tokens separados por espacios.
        No se eliminan puntuaciones; se consideran parte del token.
        
        Args:
            text: Texto a contar.
            
        Returns:
            Número de palabras.
        """
        if not text or not text.strip():
            return 0
        
        # Separar por espacios y filtrar vacíos
        words = text.split()
        return len(words)

    def extract_critical_tokens(self, text: str) -> List[str]:
        """
        Extrae tokens críticos (números, fechas, porcentajes, acrónimos).
        Estos deben preservarse exactamente en la reescritura.
        
        Args:
            text: Texto a analizar.
            
        Returns:
            Lista de tokens críticos encontrados.
        """
        critical_tokens = set()
        for pattern in self.CRITICAL_TOKENS_PATTERNS:
            matches = re.findall(pattern, text)
            critical_tokens.update(matches)
        return list(critical_tokens)

    def get_word_boundaries(self, text: str) -> List[tuple]:
        """
        Obtiene las posiciones (inicio, fin) de cada palabra.
        
        Args:
            text: Texto a analizar.
            
        Returns:
            Lista de tuplas (inicio, fin) de cada palabra.
        """
        words = text.split()
        boundaries = []
        current_pos = 0
        
        for word in words:
            start = text.find(word, current_pos)
            end = start + len(word)
            boundaries.append((start, end))
            current_pos = end
        
        return boundaries
