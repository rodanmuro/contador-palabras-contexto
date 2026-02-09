"""
ResultFormatter: formatea resultados para presentación en la interfaz.
Crea la salida final con métricas, intentos y validación.
"""

from models.dto import OutputResult, AttemptStatus
from typing import Dict, Any
import json


class ResultFormatter:
    """
    Formateador de resultados.
    Prepara datos para presentación en la interfaz web.
    """

    @staticmethod
    def format_for_web(result: OutputResult) -> Dict[str, Any]:
        """
        Formatea el resultado para presentación web (JSON).
        
        Args:
            result: Resultado de reescritura.
            
        Returns:
            Diccionario con datos formateados para la interfaz.
        """
        formatted_attempts = []
        for attempt in result.attempts:
            formatted_attempts.append({
                "attempt_number": attempt.attempt_number,
                "proposed_text": attempt.proposed_text,
                "word_count": attempt.word_count,
                "status": attempt.status.value,
                "delta": attempt.delta,
                "similarity_score": round(attempt.similarity_score, 3) if attempt.similarity_score else None,
                "hard_rules_passed": attempt.hard_rules_passed,
                "error_message": attempt.error_message
            })
        
        return {
            "success": result.status == "ACCEPTED",
            "original_text": result.original_text,
            "original_word_count": result.original_word_count,
            "final_text": result.final_text,
            "final_word_count": result.final_word_count,
            "status": result.status,
            "total_attempts": result.total_attempts,
            "validation_reason": result.validation_reason,
            "target_words": result.target_words,
            "mode": result.mode.value if result.mode else None,
            "error": result.error,
            "attempts": formatted_attempts,
            "summary": ResultFormatter._generate_summary(result)
        }

    @staticmethod
    def _generate_summary(result: OutputResult) -> str:
        """
        Genera un resumen textual del resultado.
        
        Args:
            result: Resultado de reescritura.
            
        Returns:
            Texto de resumen.
        """
        if result.status == "ACCEPTED":
            return f"""
✓ ÉXITO en {result.total_attempts} intento(s).
Palabras: {result.original_word_count} → {result.final_word_count}
Validación: {result.validation_reason}
"""
        elif result.status == "REJECTED_NO_VALID_CANDIDATE":
            return f"""
⚠ No se logró aceptación en {result.total_attempts} intento(s).
Se retorna el mejor candidato por similitud semántica.
Palabras del candidato: {result.final_word_count}
"""
        else:
            return f"""
✗ ERROR: {result.error}
"""

    @staticmethod
    def format_for_download(result: OutputResult) -> str:
        """
        Formatea el resultado para descarga (texto plano con metadatos).
        
        Args:
            result: Resultado de reescritura.
            
        Returns:
            Texto formateado para descarga.
        """
        output = f"""REPORTE DE REESCRITURA
=====================

TEXTO ORIGINAL ({result.original_word_count} palabras):
{result.original_text}

TEXTO FINAL ({result.final_word_count} palabras):
{result.final_text}

MÉTRICAS:
- Total de intentos: {result.total_attempts}
- Objetivo de palabras: {result.target_words}
- Modo: {result.mode.value if result.mode else 'N/A'}
- Estado: {result.status}
- Razón de validación: {result.validation_reason}

DETALLES DE INTENTOS:
"""
        for attempt in result.attempts:
            output += f"\n  Intento {attempt.attempt_number}:\n"
            output += f"    - Palabras: {attempt.word_count}\n"
            output += f"    - Estado: {attempt.status.value}\n"
            if attempt.delta != 0:
                output += f"    - Delta: {attempt.delta}\n"
            if attempt.similarity_score is not None:
                output += f"    - Similitud: {attempt.similarity_score:.3f}\n"
            if attempt.error_message:
                output += f"    - Error: {attempt.error_message}\n"
        
        return output
