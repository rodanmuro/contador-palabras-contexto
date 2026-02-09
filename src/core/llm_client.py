"""
LLMClient: cliente para comunicación con OpenAI API.
Maneja reescritura de textos usando modelos de lenguaje.
"""

from typing import Optional, Tuple
from models.dto import Mode


class LLMClient:
    """
    Cliente para interacción con OpenAI API.
    Responsable de:
    - Generar prompts para reescritura
    - Hacer llamadas a la API
    - Manejar reintentos y errores
    """

    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        """
        Inicializa el cliente.
        
        Args:
            api_key: Clave de API de OpenAI.
            model: Modelo a usar (gpt-4-turbo por defecto).
        """
        self.api_key = api_key
        self.model = model
        # TODO: Importar openai.Client después de instalar dependencias

    def rewrite_text(
        self,
        text: str,
        min_words: int,
        max_words: int,
        target_words: int,
        mode: Mode = Mode.BALANCED,
        delta: Optional[int] = None,
        critical_tokens: list = None,
        attempt_number: int = 1
    ) -> str:
        """
        Reescribe un texto para que quede dentro del rango de palabras.
        
        Args:
            text: Texto original.
            min_words: Mínimo de palabras requeridas.
            max_words: Máximo de palabras requeridas.
            target_words: Objetivo ideal de palabras.
            mode: Modo de reescritura (strict o balanced).
            delta: Diferencia respecto al rango (para reintentos).
            critical_tokens: Tokens que deben preservarse exactamente.
            attempt_number: Número de intento (para logging).
            
        Returns:
            Texto reescrito.
            
        Raises:
            ValueError: Si la API clave no está configurada.
            Exception: Si hay error en la llamada a la API.
        """
        if not self.api_key:
            raise ValueError("OpenAI API key no configurada")
        
        # TODO: Implementar construcción dinámico de prompt
        # TODO: Implementar llamada a OpenAI API
        # TODO: Manejar tokens límite y reintentos
        pass

    def _build_prompt(
        self,
        text: str,
        min_words: int,
        max_words: int,
        target_words: int,
        mode: Mode,
        delta: Optional[int] = None,
        critical_tokens: list = None
    ) -> str:
        """
        Construye el prompt para el LLM.
        
        Args:
            text: Texto a reescribir.
            min_words: Mínimo de palabras.
            max_words: Máximo de palabras.
            target_words: Objetivo de palabras.
            mode: Modo de reescritura.
            delta: Diferencia respecto al rango (para indicar al LLM).
            critical_tokens: Tokens a preservar.
            
        Returns:
            Prompt formateado.
        """
        prompt = f"""Por favor, reescribe el siguiente texto para que tenga entre {min_words} y {max_words} palabras (objetivo: {target_words}).

Texto original:
{text}

Instrucciones:
1. Mantén el mismo significado e intención.
2. No agregues hechos o información nueva.
3. Preserva números, fechas, porcentajes, entidades y nombres propios exactamente.
4. Modo de reescritura: {'sin cambios significativos, lo más literal posible' if mode == Mode.STRICT else 'balanceado entre literalidad y naturalidad'}.
"""
        
        if critical_tokens:
            prompt += f"5. Preserva estos tokens exactamente: {', '.join(critical_tokens)}\n"
        
        if delta and delta != 0:
            direction = "faltan" if delta > 0 else "sobran"
            prompt += f"6. Tu respuesta anterior tuvo {abs(delta)} palabras de diferencia. {direction} {abs(delta)} palabras.\n"
        
        prompt += "\nDevuelve SOLO el texto final, sin explicaciones ni listas."
        
        return prompt

    def get_embedding(self, text: str) -> list:
        """
        Obtiene el embedding (vector de embeddings) de un texto.
        
        Args:
            text: Texto a embediar.
            
        Returns:
            Vector de embeddings (lista de floats).
            
        Raises:
            ValueError: Si la API clave no está configurada.
        """
        if not self.api_key:
            raise ValueError("OpenAI API key no configurada")
        
        # TODO: Implementar llamada a embedding API
        pass
