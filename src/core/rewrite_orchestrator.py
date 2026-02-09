"""
RewriteOrchestrator: orquestador principal de reescritura.
Coordina:
- Conteo de palabras
- Llamadas a LLM con reintentos guiados
- Validaciones (duras y semántica)
- Gestión de estados y métricas
"""

from typing import Optional, List
from models.dto import (
    InputRequest, OutputResult, AttemptRecord, AttemptStatus, Mode
)
from core.word_counter import WordCounter
from core.llm_client import LLMClient
from core.validators.hard_rules import HardRulesValidator
from core.validators.semantic import SemanticValidator
from utils.logger import log_session


class RewriteOrchestrator:
    """
    Orquestador de reescritura.
    Coordina todo el flujo de reescritura con reintentos y validaciones.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        hard_rules_validator: HardRulesValidator = None,
        semantic_validator: SemanticValidator = None
    ):
        """
        Inicializa el orquestador.
        
        Args:
            llm_client: Cliente LLM para reescritura.
            hard_rules_validator: Validador de reglas duras (opcional).
            semantic_validator: Validador semántico (opcional).
        """
        self.word_counter = WordCounter()
        self.llm_client = llm_client
        self.hard_rules_validator = hard_rules_validator or HardRulesValidator()
        self.semantic_validator = semantic_validator or SemanticValidator(llm_client)

    def orchestrate(self, request: InputRequest) -> OutputResult:
        """
        Orquesta el proceso completo de reescritura.
        
        Args:
            request: Solicitud de reescritura con texto, rango y parámetros.
            
        Returns:
            Resultado final con texto reescrito, métricas e intentos.
        """
        session_id = request.session_id or "unknown"
        log_session(session_id, f"Iniciando reescritura: min={request.min_words}, max={request.max_words}")
        
        # Validar solicitud
        if not self._validate_request(request):
            return OutputResult(
                original_text=request.input_text,
                original_word_count=0,
                final_text="",
                final_word_count=0,
                status="ERROR",
                total_attempts=0,
                error="Solicitud inválida"
            )
        
        # Contar palabras originales
        original_count = self.word_counter.count(request.input_text)
        log_session(session_id, f"Conteo original: {original_count} palabras")
        
        # Si ya está dentro del rango, retornar sin cambios
        if request.min_words <= original_count <= request.max_words:
            log_session(session_id, "Texto ya está dentro del rango")
            return OutputResult(
                original_text=request.input_text,
                original_word_count=original_count,
                final_text=request.input_text,
                final_word_count=original_count,
                status="ACCEPTED",
                total_attempts=0,
                validation_reason="Ya está dentro del rango"
            )
        
        # Extraer tokens críticos a preservar
        critical_tokens = self.word_counter.extract_critical_tokens(request.input_text)
        log_session(session_id, f"Tokens críticos: {critical_tokens}")
        
        # Calcular objetivo de palabras
        target_words = self._calculate_target_words(
            original_count, request.min_words, request.max_words
        )
        
        # Ejecutar reintentos
        attempts: List[AttemptRecord] = []
        best_candidate = None
        best_similarity = -1.0
        
        for attempt_num in range(1, request.max_attempts + 1):
            log_session(session_id, f"Intento {attempt_num}/{request.max_attempts}")
            
            # Calcular delta respecto al rango
            delta = None
            if attempt_num > 1 and best_candidate:
                delta = self.word_counter.count(best_candidate) - target_words
            
            # Llamar al LLM para reescribir
            try:
                proposed_text = self.llm_client.rewrite_text(
                    text=request.input_text,
                    min_words=request.min_words,
                    max_words=request.max_words,
                    target_words=target_words,
                    mode=request.mode,
                    delta=delta,
                    critical_tokens=critical_tokens if attempt_num == 1 else None,
                    attempt_number=attempt_num
                )
            except Exception as e:
                log_session(session_id, f"Error en LLM: {str(e)}", level="ERROR")
                record = AttemptRecord(
                    attempt_number=attempt_num,
                    proposed_text="",
                    word_count=0,
                    status=AttemptStatus.OUT_OF_RANGE,
                    error_message=str(e)
                )
                attempts.append(record)
                continue
            
            # Contar palabras de la propuesta
            proposed_count = self.word_counter.count(proposed_text)
            log_session(session_id, f"Propuesta: {proposed_count} palabras")
            
            # Verificar si está dentro del rango
            in_range = request.min_words <= proposed_count <= request.max_words
            delta_actual = proposed_count - target_words
            
            if not in_range:
                record = AttemptRecord(
                    attempt_number=attempt_num,
                    proposed_text=proposed_text,
                    word_count=proposed_count,
                    status=AttemptStatus.OUT_OF_RANGE,
                    delta=delta_actual
                )
                attempts.append(record)
                best_candidate = proposed_text
                continue
            
            # Dentro del rango: verificar validaciones
            # 1. Reglas duras
            hard_rules_valid, hard_rules_reason = self.hard_rules_validator.validate(
                request.input_text, proposed_text, critical_tokens
            )
            
            if not hard_rules_valid:
                record = AttemptRecord(
                    attempt_number=attempt_num,
                    proposed_text=proposed_text,
                    word_count=proposed_count,
                    status=AttemptStatus.REJECTED_BY_HARD_RULES,
                    delta=delta_actual,
                    hard_rules_passed=False,
                    error_message=hard_rules_reason
                )
                attempts.append(record)
                best_candidate = proposed_text
                continue
            
            # 2. Similitud semántica
            threshold = (
                0.85 if request.mode == Mode.STRICT
                else 0.75
            )
            semantic_valid, similarity, semantic_reason = (
                self.semantic_validator.validate(
                    request.input_text, proposed_text, threshold
                )
            )
            
            if not semantic_valid:
                record = AttemptRecord(
                    attempt_number=attempt_num,
                    proposed_text=proposed_text,
                    word_count=proposed_count,
                    status=AttemptStatus.REJECTED_BY_SEMANTIC_SIMILARITY,
                    delta=delta_actual,
                    similarity_score=similarity,
                    error_message=semantic_reason
                )
                attempts.append(record)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_candidate = proposed_text
                continue
            
            # Validaciones pasadas: ACEPTADO
            record = AttemptRecord(
                attempt_number=attempt_num,
                proposed_text=proposed_text,
                word_count=proposed_count,
                status=AttemptStatus.ACCEPTED,
                delta=delta_actual,
                similarity_score=similarity
            )
            attempts.append(record)
            log_session(session_id, f"✓ ACEPTADO en intento {attempt_num}")
            
            # Retornar resultado exitoso
            return OutputResult(
                original_text=request.input_text,
                original_word_count=original_count,
                final_text=proposed_text,
                final_word_count=proposed_count,
                status="ACCEPTED",
                total_attempts=attempt_num,
                attempts=attempts,
                validation_reason="Pasó todas las validaciones",
                target_words=target_words,
                mode=request.mode,
                session_id=session_id
            )
        
        # Fin de reintentos sin aceptación
        log_session(session_id, f"No se logró aceptación en {request.max_attempts} intentos")
        
        # Retornar mejor candidato o error
        if best_candidate:
            return OutputResult(
                original_text=request.input_text,
                original_word_count=original_count,
                final_text=best_candidate,
                final_word_count=self.word_counter.count(best_candidate),
                status="REJECTED_NO_VALID_CANDIDATE",
                total_attempts=request.max_attempts,
                attempts=attempts,
                validation_reason="No cumplió validaciones en los intentos realizados",
                target_words=target_words,
                mode=request.mode,
                session_id=session_id,
                error="Se retorna mejor candidato por similitud"
            )
        else:
            return OutputResult(
                original_text=request.input_text,
                original_word_count=original_count,
                final_text="",
                final_word_count=0,
                status="ERROR",
                total_attempts=request.max_attempts,
                attempts=attempts,
                mode=request.mode,
                session_id=session_id,
                error="No se pudo generar propuestas válidas"
            )

    def _validate_request(self, request: InputRequest) -> bool:
        """Valida que la solicitud tenga parámetros válidos."""
        if not request.input_text or len(request.input_text) == 0:
            return False
        if request.min_words < 1 or request.max_words < request.min_words:
            return False
        if request.max_attempts < 1:
            return False
        return True

    def _calculate_target_words(
        self,
        original_count: int,
        min_words: int,
        max_words: int
    ) -> int:
        """
        Calcula el objetivo de palabras basado en el conteo original.
        
        Estrategia:
        - Si original < min: apuntar al mínimo
        - Si original > max: apuntar al máximo
        """
        if original_count < min_words:
            return min_words
        elif original_count > max_words:
            return max_words
        else:
            return original_count
