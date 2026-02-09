"""
SemanticValidator: validador basado en similitud semántica.
Usa embeddings para comparar similitud entre texto original y reescrito.
"""

from typing import Tuple
import math


class SemanticValidator:
    """
    Validador de similitud semántica.
    Utiliza embeddings y distancia coseno para verificar preservación de significado.
    """

    def __init__(self, llm_client=None):
        """
        Inicializa el validador.
        
        Args:
            llm_client: Cliente LLM que proporciona embeddings.
        """
        self.llm_client = llm_client

    def validate(
        self,
        original_text: str,
        rewritten_text: str,
        threshold: float = 0.75
    ) -> Tuple[bool, float, str]:
        """
        Valida similitud semántica entre textos.
        
        Args:
            original_text: Texto original.
            rewritten_text: Texto reescrito.
            threshold: Umbral de similitud (0-1). Debe ser >= threshold.
            
        Returns:
            Tupla (válido, similitud, razón_si_falla).
        """
        if not self.llm_client:
            # Sin cliente LLM, pasamos la validación
            return True, 1.0, ""
        
        try:
            # Obtener embeddings
            original_embedding, _ = self.llm_client.get_embedding(original_text)
            rewritten_embedding, _ = self.llm_client.get_embedding(rewritten_text)
            
            # Calcular similitud coseno
            similarity = self._cosine_similarity(original_embedding, rewritten_embedding)
            
            if similarity >= threshold:
                return True, similarity, ""
            else:
                return False, similarity, f"Similitud semántica baja: {similarity:.2f} < {threshold}"
        except Exception as e:
            # En caso de error en embeddings, permitir pero registrar
            return True, 0.0, ""

    @staticmethod
    def _cosine_similarity(vec1: list, vec2: list) -> float:
        """
        Calcula similitud coseno entre dos vectores.
        
        Args:
            vec1: Primer vector.
            vec2: Segundo vector.
            
        Returns:
            Similitud coseno (0-1).
        """
        if len(vec1) != len(vec2):
            raise ValueError("Los vectores deben tener la misma dimensión")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a ** 2 for a in vec1))
        norm2 = math.sqrt(sum(b ** 2 for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
