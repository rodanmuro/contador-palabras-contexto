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
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

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
