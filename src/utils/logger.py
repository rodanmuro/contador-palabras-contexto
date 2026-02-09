"""
Logger: configuración de logging estructurado.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from config import LOG_LEVEL, LOG_FILE


class StructuredLogger:
    """Logger estructurado con soporte para sesiones y contexto."""

    def __init__(self, name: str, log_file: str = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL))

        # Formato con timestamp e identificador de sesión
        formatter = logging.Formatter(
            '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler a archivo
        if log_file is None:
            log_file = LOG_FILE
        
        os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Handler a consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


# Instancia global del logger
_logger = StructuredLogger(__name__).get_logger()


def get_logger(name: str = None):
    """Obtiene una instancia del logger."""
    if name:
        return logging.getLogger(name)
    return _logger


def log_session(session_id: str, message: str, level: str = "INFO"):
    """Registra un evento con identificador de sesión."""
    log_func = getattr(_logger, level.lower(), _logger.info)
    log_func(f"[Session {session_id}] {message}")
