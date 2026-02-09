"""
Modelos de Datos (DTOs): estructuras para entrada/salida.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
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
class TokenMetrics:
    """Métricas de tokens y costo de una petición LLM."""
    input_tokens: int = 0
    cached_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    model: str = ""
    
    @property
    def total_tokens(self) -> int:
        """Calcula total de tokens como suma de input + cached + output."""
        return self.input_tokens + self.cached_tokens + self.output_tokens
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte métricas a diccionario."""
        return {
            "input_tokens": self.input_tokens,
            "cached_tokens": self.cached_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "model": self.model
        }


@dataclass
class InputRequest:
    """DTO para solicitud de reescritura."""
    input_text: str
    min_words: int
    max_words: int
    model: str = "gpt-4o-mini"
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
    token_metrics: Optional[TokenMetrics] = None


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
    model: str = "gpt-4o-mini"
    
    # Nuevos campos para tracking de costos
    total_token_metrics: Optional[TokenMetrics] = None
    total_cost_usd: float = 0.0
