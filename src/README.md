# Word-Range Rewriter - Documentación Técnica

## Descripción
Aplicación web para reescribir textos (enunciados/contextos de preguntas de selección múltiple) dentro de rangos de palabras específicos, manteniendo significado semántico usando OpenAI API.

## Estructura de Directorios

```
src/
├── app.py                      # Punto de entrada Flask
├── config.py                   # Configuración global
├── requirements.txt            # Dependencias Python
├── .gitignore                  # Archivos a ignorar en Git
├── .env.example                # Template de variables de entorno
│
├── core/                       # Lógica principal
│   ├── word_counter.py         # WordCounter: conteo determinístico
│   ├── llm_client.py           # LLMClient: orquestación OpenAI
│   ├── rewrite_orchestrator.py # RewriteOrchestrator: flujo principal
│   └── validators/
│       ├── hard_rules.py       # HardRulesValidator: reglas duras
│       └── semantic.py         # SemanticValidator: similitud semántica
│
├── models/                     # Estructuras de datos
│   └── dto.py                  # InputRequest, OutputResult, AttemptRecord
│
├── web/                        # Interfaz web
│   ├── routes.py               # Endpoints Flask
│   └── result_formatter.py     # Formateo de resultados
│
├── templates/                  # HTML templates
│   └── index.html              # Página principal
│
├── static/                     # Recursos estáticos
│   ├── app.js                  # JavaScript del cliente
│   └── style.css               # Estilos CSS
│
├── utils/                      # Utilidades
│   └── logger.py               # Logging estructurado
│
└── tests/                      # Suite de tests
    ├── test_word_counter.py
    ├── test_validators.py
    └── test_orchestrator.py
```

## Requisitos Previos

- Python 3.8+
- pip (gestor de paquetes)
- OpenAI API key
- (Opcional) Virtual environment (venv)

## Instalación

### 1. Preparar entorno virtual
```bash
cd src/
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
# Crear archivo .env basado en el template
cp .env.example .env

# Editar .env y agregar tu OpenAI API key
# OPENAI_API_KEY=sk-...
```

## Ejecución

### Modo desarrollo
```bash
python app.py
```

Acceder a: `http://127.0.0.1:5000`

### Modo producción
```bash
# Usar un WSGI server como Gunicorn
pip install gunicorn
gunicorn -w 4 app:create_app()
```

## Estructura del Flujo de Reescritura

```
InputRequest
    ↓
[WordCounter.count()] → Contar palabras originales
    ↓
¿Dentro de rango? → Sí → return ACCEPTED
    ↓ No
[Extraer tokens críticos]
    ↓
[Calcular target_words]
    ↓
Para cada intento (1 a max_attempts):
    ├─ [LLMClient.rewrite_text()] → Llamar OpenAI
    ├─ [WordCounter.count()] → Contar propuesta
    ├─ ¿Dentro de rango? → No → siguiente intento
    │
    ├─ [HardRulesValidator.validate()] → Verificar reglas duras
    │  ├─ ¿Válido? → No → siguiente intento
    │  └─ ¿Válido? → Sí → continuar
    │
    ├─ [SemanticValidator.validate()] → Verificar similitud
    │  ├─ ¿Válido? → No → guardar como "best" e ir a siguiente intento
    │  └─ ¿Válido? → Sí → return ACCEPTED
    │
    └─ Fin de intento
    ↓
return REJECTED o mejor candidato
```

## API Endpoints

### GET `/`
Retorna la página principal (interfaz web).

### POST `/api/rewrite`
Reescribe un texto.

**Request:**
```json
{
    "input_text": "Texto a reescribir...",
    "min_words": 10,
    "max_words": 50,
    "mode": "balanced",
    "max_attempts": 5
}
```

**Response:**
```json
{
    "success": true/false,
    "original_text": "...",
    "original_word_count": 25,
    "final_text": "...",
    "final_word_count": 30,
    "status": "ACCEPTED",
    "total_attempts": 2,
    "validation_reason": "...",
    "attempts": [...],
    "error": null
}
```

### POST `/api/download`
Descarga el reporte en formato texto plano.

**Request:** Igual a `/api/rewrite`

**Response:** Archivo `.txt` con reporte detallado.

### GET `/api/health`
Chequeo de salud de la aplicación.

## Patrones de Diseño

### 1. **Inyección de Dependencias**
- `RewriteOrchestrator` recibe sus dependencias (LLMClient, Validators) en el constructor
- Facilita testing y cambios de implementación

### 2. **DTOs (Data Transfer Objects)**
- `InputRequest`, `OutputResult`, `AttemptRecord` encapsulan datos
- Separación clara entre capas

### 3. **Factory Pattern**
- `create_routes()` crea rutas con inyección de dependencias
- `create_app()` crea la aplicación Flask

### 4. **Single Responsibility**
- Cada clase tiene una responsabilidad única:
  - `WordCounter`: conteo
  - `LLMClient`: comunicación LLM
  - `HardRulesValidator`: validación determinística
  - `SemanticValidator`: validación semántica
  - `RewriteOrchestrator`: orquestación del flujo

## Testing

Ejecutar todos los tests:
```bash
python -m pytest tests/ -v
```

Cobertura de tests:
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

## Configuración

Parámetros configurables en `.env`:

- `OPENAI_API_KEY`: Clave de API de OpenAI (requerida)
- `DEFAULT_MAX_ATTEMPTS`: Número máximo de intentos (default: 5)
- `SIMILARITY_THRESHOLD_STRICT`: Umbral en modo estricto (default: 0.85)
- `SIMILARITY_THRESHOLD_BALANCED`: Umbral en modo balanceado (default: 0.75)
- `LOG_LEVEL`: Nivel de logging (default: INFO)
- `MAX_INPUT_CHARS`: Máximo de caracteres permitidos (default: 5000)

## Consideraciones de Seguridad

- ✅ Sanitización de entrada (length limits)
- ✅ Rate limiting configurables
- ✅ Logging de sesiones para auditoría
- ✅ Variables de entorno para secrets
- ✅ CSRF protection en formularios (agregar en fase de producción)

## Próximas Fases

### Fase 2
- Tokens críticos configurables por usuario
- Reporte de cambios detectados
- Historial de versiones

### Fase 3
- Streaming con detención automática en rango
- Edición colaborativa
- Almacenamiento de versiones

## Troubleshooting

### Error: "OpenAI API key no configurada"
→ Verificar que `OPENAI_API_KEY` esté en `.env`

### Error: "Module not found"
→ Ejecutar `pip install -r requirements.txt`

### Error: "Port already in use"
→ Cambiar `PORT` en `.env` o matar proceso en puerto 5000

## Contacto y Soporte

Para preguntas o reportes de bugs, contactar al equipo de desarrollo.
