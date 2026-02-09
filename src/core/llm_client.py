"""
LLMClient: cliente para comunicación con OpenAI API.
Maneja reescritura de textos usando modelos de lenguaje.
"""

from typing import Optional, Tuple
from openai import OpenAI
from models.dto import Mode, TokenMetrics
from config import AVAILABLE_MODELS


class LLMClient:
    """
    Cliente para interacción con OpenAI API.
    Responsable de:
    - Generar prompts para reescritura
    - Hacer llamadas a la API
    - Rastrear tokens y costos
    - Manejar reintentos y errores
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Inicializa el cliente.
        
        Args:
            api_key: Clave de API de OpenAI.
            model: Modelo a usar (gpt-4o-mini por defecto).
        """
        self.api_key = api_key
        self.model = model
        self.model_config = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS["gpt-4o-mini"])
        self.client = OpenAI(api_key=api_key)

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
    ) -> Tuple[str, Optional[TokenMetrics]]:
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
            Tupla (texto_reescrito, métricas_de_tokens).
            
        Raises:
            ValueError: Si la API clave no está configurada.
            Exception: Si hay error en la llamada a la API.
        """
        if not self.api_key:
            raise ValueError("OpenAI API key no configurada")
        
        # Construir prompt
        prompt = self._build_prompt(
            text, min_words, max_words, target_words, mode, delta, critical_tokens
        )
        
        try:
            # Hacer llamada a OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en reescritura de textos. Sigue las instrucciones exactamente."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extraer texto de la respuesta
            rewritten_text = response.choices[0].message.content.strip()
            
            # Extraer tokens de la respuesta
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            # Los cached_tokens no siempre están en la respuesta, usar 0 si no existe
            cached_tokens = getattr(response.usage, 'cache_read_input_tokens', 0) or 0
            
            # Crear TokenMetrics
            token_metrics = TokenMetrics(
                input_tokens=input_tokens,
                cached_tokens=cached_tokens,
                output_tokens=output_tokens,
                model=self.model
            )
            
            # Calcular costo
            token_metrics.cost_usd = self._calculate_cost(token_metrics)
            
            return rewritten_text, token_metrics
            
        except Exception as e:
            raise Exception(f"Error en reescritura LLM: {str(e)}")

    def get_embedding(self, text: str) -> Tuple[list, Optional[TokenMetrics]]:
        """
        Obtiene el embedding (vector de embeddings) de un texto.
        
        Args:
            text: Texto a embediar.
            
        Returns:
            Tupla (vector_embeddings, métricas_de_tokens).
            
        Raises:
            ValueError: Si la API clave no está configurada.
        """
        if not self.api_key:
            raise ValueError("OpenAI API key no configurada")
        
        try:
            # Hacer llamada a embedding API
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            # Extraer embedding del response
            embedding = response.data[0].embedding
            
            # Extraer tokens
            input_tokens = response.usage.prompt_tokens
            
            # Crear TokenMetrics para embedding
            token_metrics = TokenMetrics(
                input_tokens=input_tokens,
                cached_tokens=0,
                output_tokens=0,
                model="text-embedding-3-small"
            )
            
            # Calcular costo (embeddings tienen precios específicos)
            # Costo de embedding: $0.02 por 1M tokens
            token_metrics.cost_usd = (input_tokens * 0.02) / 1_000_000
            
            return embedding, token_metrics
            
        except Exception as e:
            raise Exception(f"Error en embedding LLM: {str(e)}")

    def _calculate_cost(self, token_metrics: TokenMetrics) -> float:
        """
        Calcula el costo en USD basado en tokens y modelo.
        
        Args:
            token_metrics: Métricas de tokens.
            
        Returns:
            Costo en USD.
        """
        pricing = self.model_config["pricing"]
        
        # Costo = (input_tokens * precio_input + cached_tokens * precio_cached + output_tokens * precio_output) / 1,000,000
        # Los precios están en USD por 1 millón de tokens
        cost = (
            (token_metrics.input_tokens * pricing["input"]) +
            (token_metrics.cached_tokens * pricing["cached"]) +
            (token_metrics.output_tokens * pricing["output"])
        ) / 1_000_000
        
        return cost

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
