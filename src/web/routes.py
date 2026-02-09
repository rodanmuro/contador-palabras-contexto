"""
Routes: rutas Flask para la aplicación web.
Expone endpoints para reescritura, validación y descarga.
"""

from flask import Blueprint, request, jsonify, render_template, send_file
from io import StringIO
from datetime import datetime
import uuid

from models.dto import InputRequest, Mode
from core.rewrite_orchestrator import RewriteOrchestrator
from web.result_formatter import ResultFormatter
from utils.logger import get_logger, log_session


logger = get_logger(__name__)
bp = Blueprint('main', __name__)


def create_routes(orchestrator: RewriteOrchestrator):
    """
    Factory para crear rutas con inyección de dependencias.
    
    Args:
        orchestrator: Instancia de RewriteOrchestrator.
    """

    @bp.route('/', methods=['GET'])
    def index():
        """Página principal con formulario."""
        return render_template('index.html')

    @bp.route('/api/rewrite', methods=['POST'])
    def rewrite():
        """
        Endpoint para reescribir texto.
        
        Body JSON:
        {
            "input_text": "texto a reescribir",
            "min_words": 10,
            "max_words": 50,
            "mode": "balanced || strict",
            "max_attempts": 5
        }
        
        Retorna:
        {
            "success": boolean,
            "final_text": "texto reescrito",
            "original_word_count": int,
            "final_word_count": int,
            "total_attempts": int,
            ...
        }
        """
        try:
            data = request.get_json()
            session_id = str(uuid.uuid4())[:8]
            
            log_session(session_id, "Solicitud de reescritura recibida")
            
            # Validar campos obligatorios
            if not data.get('input_text'):
                return jsonify({"error": "input_text es obligatorio"}), 400
            if not isinstance(data.get('min_words'), int) or not isinstance(data.get('max_words'), int):
                return jsonify({"error": "min_words y max_words deben ser números"}), 400
            
            # Construir solicitud
            mode_str = data.get('mode', 'balanced').lower()
            mode = Mode.STRICT if mode_str == 'strict' else Mode.BALANCED
            
            input_request = InputRequest(
                input_text=data['input_text'],
                min_words=data['min_words'],
                max_words=data['max_words'],
                mode=mode,
                max_attempts=data.get('max_attempts', 5),
                session_id=session_id
            )
            
            # Ejecutar orquestación
            result = orchestrator.orchestrate(input_request)
            
            # Formatear respuesta
            formatted = ResultFormatter.format_for_web(result)
            log_session(session_id, f"Reescritura completada: {result.status}")
            
            return jsonify(formatted), 200
        
        except Exception as e:
            logger.error(f"Error en /api/rewrite: {str(e)}", exc_info=True)
            return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

    @bp.route('/api/download', methods=['POST'])
    def download():
        """
        Endpoint para descargar resultado en formato texto.
        
        Body JSON: { ...mismo que /api/rewrite }
        
        Retorna: archivo de texto con reporte.
        """
        try:
            data = request.get_json()
            session_id = str(uuid.uuid4())[:8]
            
            log_session(session_id, "Solicitud de descarga")
            
            # Construir y ejecutar solicitud
            mode_str = data.get('mode', 'balanced').lower()
            mode = Mode.STRICT if mode_str == 'strict' else Mode.BALANCED
            
            input_request = InputRequest(
                input_text=data['input_text'],
                min_words=data['min_words'],
                max_words=data['max_words'],
                mode=mode,
                max_attempts=data.get('max_attempts', 5),
                session_id=session_id
            )
            
            result = orchestrator.orchestrate(input_request)
            formatted_text = ResultFormatter.format_for_download(result)
            
            # Crear archivo de descarga
            bytes_io = StringIO(formatted_text)
            filename = f"reescritura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            return send_file(
                StringIO(formatted_text),
                as_attachment=True,
                download_name=filename,
                mimetype="text/plain"
            )
        
        except Exception as e:
            logger.error(f"Error en /api/download: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @bp.route('/api/health', methods=['GET'])
    def health():
        """Chequeo de salud de la aplicación."""
        return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()}), 200

    return bp
