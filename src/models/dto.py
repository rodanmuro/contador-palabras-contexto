"""
Modelos de Datos (DTOs): estructuras para entrada/salida.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class Mode(str, Enum):
    """Modos de reescritura."""
    STRICT = "strict"
    BALANCED = "balanced"


class AttemptStatus(str, Enum):
    """Estados posibles por intento de reescritura."""
    OUT_OF_RANGE = "OUT_OF_RANGE"
    IN_RANGE_PENDING_VALIDATION = "IN_RANGE_PENDING_VALIDATION"
    REJECTED_BY_HARD_RULES = "REJECTED_BY_HARD_RULES"
    REJECTED_BY_SEMANTIC_SIMILARITY = "REJECTED_BY_SEMANTIC_SIMILARITY"
    ACCEPTED = "ACCEPTED"


@dataclass
class InputRequest:
    """DTO para solicitud de reescritura."""
    input_text: str
    min_words: int
    max_words: int
    mode: Mode = Mode.BALANCED
    max_attempts: int = 5
    session_id: Optional[str] = None


@dataclass
class AttemptRecord:
    """Registro de un intento individual de reescritura."""
    attempt_number: int
    proposed_text: str
    word_count: int
    status: AttemptStatus
    delta: int = 0  # Diferencia entre conteo y rango
    similarity_score: Optional[float] = None
    hard_rules_passed: bool = True
    error_message: Optional[str] = None


@dataclass
class OutputResult:
    """DTO para resultado final de reescritura."""
    original_text: str
    original_word_count: int
    final_text: str
    final_word_count: int
    status: str  # "ACCEPTED" o "REJECTED_NO_VALID_CANDIDATE"
    total_attempts: int
    attempts: List[AttemptRecord] = field(default_factory=list)
    validation_reason: str = ""
    target_words: Optional[int] = None
    mode: Mode = Mode.BALANCED
    session_id: Optional[str] = None
    error: Optional[str] = None
