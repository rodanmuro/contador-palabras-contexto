"""
Configuración de la aplicación.
Variables de entorno, constantes y parámetros globales.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Flask
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 5000))

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Modelos disponibles con precios (USD por 1M tokens)
AVAILABLE_MODELS = {
    "gpt-4o-mini": {
        "display_name": "GPT-4o Mini (Recomendado)",
        "api_name": "gpt-4o-mini",
        "pricing": {
            "input": 0.15,
            "cached": 0.075,
            "output": 0.60
        }
    },
    "gpt-3.5-turbo": {
        "display_name": "GPT-3.5 Turbo (Económico)",
        "api_name": "gpt-3.5-turbo",
        "pricing": {
            "input": 0.50,
            "cached": 0.25,
            "output": 1.50
        }
    },
    "gpt-4.1-mini": {
        "display_name": "GPT-4.1 Mini",
        "api_name": "gpt-4.1-mini",
        "pricing": {
            "input": 0.40,
            "cached": 0.10,
            "output": 1.60
        }
    },
    "gpt-4.1": {
        "display_name": "GPT-4.1 (Potente)",
        "api_name": "gpt-4.1",
        "pricing": {
            "input": 2.00,
            "cached": 0.50,
            "output": 8.00
        }
    },
    "gpt-4o": {
        "display_name": "GPT-4o (Más potente)",
        "api_name": "gpt-4o",
        "pricing": {
            "input": 5.00,
            "cached": 2.50,
            "output": 15.00
        }
    }
}
DEFAULT_MODEL = "gpt-4o-mini"

# Word Counter
# Definición: separación por espacios, manejo de signos
WORD_COUNTER_STRATEGY = os.getenv("WORD_COUNTER_STRATEGY", "whitespace")

# Rewrite Orchestrator
DEFAULT_MAX_ATTEMPTS = int(os.getenv("DEFAULT_MAX_ATTEMPTS", 5))
DEFAULT_MODE = os.getenv("DEFAULT_MODE", "balanced")  # "strict" o "balanced"

# Validators
SIMILARITY_THRESHOLD_STRICT = float(os.getenv("SIMILARITY_THRESHOLD_STRICT", 0.85))
SIMILARITY_THRESHOLD_BALANCED = float(os.getenv("SIMILARITY_THRESHOLD_BALANCED", 0.75))

# Input constraints
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", 5000))
MIN_WORDS = int(os.getenv("MIN_WORDS", 5))
MAX_WORDS = int(os.getenv("MAX_WORDS", 2000))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")

# Session timeout (en segundos)
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 3600))

# Rate limiting (requests por minuto)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 30))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))

# Costo de embeddings (para similitud semántica)
EMBEDDING_COST_PER_MTK = 0.02  # $0.02 por millón de tokens para text-embedding-3-small
