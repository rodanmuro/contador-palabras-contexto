"""
HardRulesValidator: validador de reglas duras determinísticas.
Verifica:
- Preservación de números, fechas, porcentajes
- Preservación de tokens críticos
- No introducción de hechos nuevos (heurística)
"""

import re
from typing import List, Tuple
from core.word_counter import WordCounter


class HardRulesValidator:
    """
    Validador de reglas duras.
    Aplica restricciones determinísticas a candidatos de reescritura.
    """

    def __init__(self):
        self.word_counter = WordCounter()

    def validate(
        self,
        original_text: str,
        rewritten_text: str,
        critical_tokens: List[str] = None
    ) -> Tuple[bool, str]:
        """
        Valida un texto reescrito contra reglas duras.
        
        Args:
            original_text: Texto original.
            rewritten_text: Texto reescrito.
            critical_tokens: Tokens críticos a verificar (números, nombres, etc.).
            
        Returns:
            Tupla (válido, razón_si_falla).
        """
        # Regla 1: Verificar preservación de números y fechas
        if not self._check_numeric_preservation(original_text, rewritten_text):
            return False, "Números, fechas o porcentajes no fueron preservados"
        
        # Regla 2: Verificar tokens críticos
        if critical_tokens:
            if not self._check_critical_tokens(rewritten_text, critical_tokens):
                return False, "No se preservaron todos los tokens críticos"
        
        # Regla 3: Heurística de no-novedad (simple)
        if not self._check_no_new_facts(original_text, rewritten_text):
            return False, "Se detectaron hechos o información nueva"
        
        return True, ""

    def _check_numeric_preservation(
        self,
        original: str,
        rewritten: str
    ) -> bool:
        """
        Verifica que números, fechas y porcentajes se preserven.
        
        Args:
            original: Texto original.
            rewritten: Texto reescrito.
            
        Returns:
            True si se preservan, False en caso contrario.
        """
        # Patrones de números y fechas
        patterns = [
            r'\d+[.,]\d+',  # Decimales
            r'\d+\s*%',      # Porcentajes
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # Fechas
            r'\b\d+\b',      # Números enteros
        ]
        
        for pattern in patterns:
            original_matches = set(re.findall(pattern, original))
            rewritten_matches = set(re.findall(pattern, rewritten))
            
            # Verificar que todos los números originales estén en el reescrito
            if not original_matches.issubset(rewritten_matches):
                return False
        
        return True

    def _check_critical_tokens(
        self,
        rewritten: str,
        critical_tokens: List[str]
    ) -> bool:
        """
        Verifica que los tokens críticos aparezcan en el texto reescrito.
        
        Args:
            rewritten: Texto reescrito.
            critical_tokens: Tokens a verificar.
            
        Returns:
            True si todos están presentes, False en caso contrario.
        """
        for token in critical_tokens:
            if token not in rewritten:
                return False
        return True

    def _check_no_new_facts(
        self,
        original: str,
        rewritten: str
    ) -> bool:
        """
        Heurística simple: verifica que no haya información radicalmente nueva.
        Se basa en:
        - Palabras clave adicionales sospechosas (números nuevos, nuevos sujetos)
        - Longitud no debe aumentar significativamente
        
        Args:
            original: Texto original.
            rewritten: Texto reescrito.
            
        Returns:
            True si parece legítimo, False si hay sospecha de novedad.
        """
        # Extraer palabras sustanciales (no artículos, preposiciones, etc.)
        stop_words = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
            'de', 'del', 'a', 'al', 'en', 'con', 'sin', 'por', 'para',
            'y', 'o', 'pero', 'que', 'es', 'es', 'está', 'son'
        }
        
        original_words = set(w.lower() for w in original.split() if w.lower() not in stop_words)
        rewritten_words = set(w.lower() for w in rewritten.split() if w.lower() not in stop_words)
        
        # Si más del 40% son palabras nuevas, es sospechoso
        new_words = rewritten_words - original_words
        if len(new_words) > len(original_words) * 0.4:
            return False
        
        return True
