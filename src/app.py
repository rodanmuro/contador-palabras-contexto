"""
Punto de entrada de la aplicación Flask.
Configura y lanza el servidor web.
"""

from flask import Flask
from config import DEBUG, HOST, PORT, SECRET_KEY, LOG_LEVEL
from core.llm_client import LLMClient
from core.rewrite_orchestrator import RewriteOrchestrator
from core.validators.hard_rules import HardRulesValidator
from core.validators.semantic import SemanticValidator
from web.routes import create_routes
from utils.logger import get_logger
import os

logger = get_logger(__name__)


def create_app():
    """Factory para crear la aplicación Flask."""
    
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    
    logger.info(f"Aplicación creada. Debug: {DEBUG}, Log Level: {LOG_LEVEL}")
    
    # Inyectar dependencias
    llm_client = LLMClient(
        api_key=os.getenv('OPENAI_API_KEY', ''),
        model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo')
    )
    
    hard_rules_validator = HardRulesValidator()
    semantic_validator = SemanticValidator(llm_client)
    
    orchestrator = RewriteOrchestrator(
        llm_client=llm_client,
        hard_rules_validator=hard_rules_validator,
        semantic_validator=semantic_validator
    )
    
    # Registrar rutas
    routes_bp = create_routes(orchestrator)
    app.register_blueprint(routes_bp)
    
    logger.info("Rutas registradas exitosamente")
    
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info(f"Iniciando servidor en {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
