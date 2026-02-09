# Spec-Driven Development (SDD) — Word-Range Rewriter para Ítems de Selección Múltiple

## 1) Objetivo
Construir una aplicación web simple que reciba un texto (enunciado/contexto de una pregunta de selección múltiple) y un rango de palabras aceptable, y produzca una versión reescrita que:
- Cumpla el rango de palabras **[minWords, maxWords]**.
- Mantenga el **mismo significado semántico** y el **contexto** del texto original.
- Minimice deriva semántica, costos y latencia mediante control de reintentos y validaciones.

## 2) Alcance
### Incluye
- Interfaz web mínima (textarea + inputs + botón + salida).
- Conteo de palabras determinístico (hard-code).
- Orquestación de reescritura con LLM (OpenAI API) con reintentos controlados.
- Validaciones de fidelidad (reglas duras + similitud semántica).
- Registro básico de métricas (iteraciones, conteos, estado final).

### No incluye (por ahora)
- Streaming token a token para corte por palabras (se considera fase futura).
- Gestión avanzada de usuarios/roles/SSO.
- Edición colaborativa, historial largo de versiones o almacenamiento complejo.
- Generación completa del ítem (solo ajuste del texto dado).

## 3) Usuarios y casos de uso
### Usuario principal
- Docente/creador de ítems que necesita ajustar el largo del contexto/enunciado sin cambiar la intención.

### Casos de uso
1. Pegar texto + definir minWords/maxWords + generar versión ajustada.
2. Ver conteo original vs conteo final y número de iteraciones.
3. Ajustar “modo” de reescritura: **Estricto** (más literal) vs **Fluido** (más natural sin agregar hechos).
4. Descargar/copiar el resultado final.

## 4) Requerimientos funcionales
### RF-1 Ingreso de datos
- El sistema debe recibir:
  - `inputText` (texto original)
  - `minWords`, `maxWords` (rango inclusivo)
  - `mode` ∈ {`strict`, `balanced`} (opcional; default `balanced`)
  - `maxAttempts` (opcional; default 4–6)

### RF-2 Conteo determinístico de palabras
- El sistema debe calcular `wordCount(inputText)` de forma consistente.
- Debe definir claramente qué se considera “palabra” (separación por espacios, manejo de signos, etc.).

### RF-3 Reescritura por LLM con objetivo de rango
- Si `wordCount(inputText)` está dentro del rango, devolver sin cambios (o permitir “normalizar estilo” opcional en modo futuro).
- Si está fuera:
  - Calcular un `targetWords` (p. ej. cercano a `minWords` si falta, o `maxWords` si sobra).
  - Enviar al LLM instrucciones explícitas de:
    - mantener significado,
    - no agregar hechos nuevos,
    - preservar entidades/valores,
    - devolver solo el texto final.

### RF-4 Reintentos guiados por delta de palabras
- Tras recibir una propuesta del LLM:
  - Recontar palabras con hard-code.
  - Si no cumple rango, reintentar indicando el delta exacto: “faltan/sobran K palabras”.
- Detener al cumplir rango o al alcanzar `maxAttempts`.

### RF-5 Validación de fidelidad (anti-deriva)
- Antes de aceptar un resultado dentro del rango, aplicar:
  1) **Reglas duras** (determinísticas):
     - preservar números/porcentajes/fechas exactas,
     - preservar tokens críticos (lista derivada del texto: nombres propios, términos técnicos relevantes),
     - no introducir afirmaciones nuevas evidentes (heurística).
  2) **Similitud semántica**:
     - calcular similitud entre original y candidato usando embeddings,
     - exigir umbral configurable por modo (strict más alto).
- Si falla fidelidad, reintentar con advertencia “más literal, sin cambios de hechos”.

### RF-6 Salida y trazabilidad mínima
- Mostrar:
  - texto final,
  - conteo original y final,
  - número de intentos,
  - estado de validación (aprobado/rechazado) y razón resumida.

## 5) Requerimientos no funcionales
- Latencia: objetivo < 10–15 s en la mayoría de casos (dependiente de API).
- Robustez: nunca iterar indefinidamente; siempre respetar `maxAttempts`.
- Observabilidad: logs con identificador de sesión, intentos y métricas.
- Seguridad: sanitizar entradas para evitar inyección en logs/vistas; rate limiting básico.
- Privacidad: no almacenar textos si no se requiere; modo “no persistente” por defecto.

## 6) Principios de diseño
- El conteo de palabras es **autoridad** del sistema (no del LLM).
- Minimizar cambios: preferir reescritura local, evitar agregar información nueva.
- Evitar “corte” por streaming en fase 1 (riesgo de incoherencia).
- Validación semántica como compuerta de calidad antes de entregar.

## 7) Estrategia de prompting (nivel conceptual)
### Instrucciones base al LLM
- Mantén el mismo significado e intención.
- No agregues hechos ni cambies condiciones.
- Preserva números, unidades, fechas, nombres propios.
- Ajusta el texto para quedar entre `minWords` y `maxWords`, apuntando a `targetWords`.
- Devuelve solo el texto final (sin listas, sin explicaciones).

### Instrucciones en reintentos
- Tu salida tuvo `N` palabras; ajusta para estar en rango; te faltan/sobran `K` palabras.
- Mantén fidelidad; si hubo deriva, “hazlo más literal”.

## 8) Tecnología propuesta
- Backend: **Python + Flask** (monolito).
- Frontend: templates Jinja (vistas simples), HTML/CSS mínimo.
- LLM: **OpenAI API** (chat completions) para reescritura.
- Embeddings: **OpenAI embeddings** para similitud semántica.
- Configuración: variables de entorno (API keys, umbrales, maxAttempts).
- Observabilidad: logging estándar (archivo o stdout).

## 9) Componentes (conceptuales)
- `Web UI`: formulario de entrada y panel de resultados.
- `Controller`: valida inputs, orquesta flujo de reescritura.
- `WordCounter`: conteo determinístico.
- `RewriteOrchestrator`: ejecuta intentos con deltas.
- `HardRulesValidator`: números/tokens críticos/no-novedad heurística.
- `SemanticValidator`: embeddings + similitud coseno.
- `ResultFormatter`: compone salida y métricas.

## 10) Datos y configuración
- Parámetros configurables:
  - `DEFAULT_MAX_ATTEMPTS`
  - `SIMILARITY_THRESHOLD_STRICT`
  - `SIMILARITY_THRESHOLD_BALANCED`
  - `MAX_INPUT_CHARS`
- Derivación de tokens críticos:
  - extraer candidatos (nombres propios, números, términos largos, acrónimos) y permitir ajuste manual en fase futura.

## 11) Estados y decisiones
### Estados por intento
- `OUT_OF_RANGE` (por conteo)
- `IN_RANGE_PENDING_VALIDATION`
- `REJECTED_BY_HARD_RULES`
- `REJECTED_BY_SEMANTIC_SIMILARITY`
- `ACCEPTED`

### Política de salida
- Si `ACCEPTED`: devolver candidato final.
- Si no se logra aceptación en `maxAttempts`:
  - devolver el “mejor candidato” (mayor similitud dentro del rango) o, alternativamente, devolver error controlado según configuración.

## 12) Criterios de aceptación (Definition of Done)
- Dado un texto y un rango, el sistema:
  - devuelve un texto dentro del rango en la mayoría de casos,
  - preserva números/entidades,
  - rechaza variantes con baja similitud,
  - respeta `maxAttempts` sin bucles infinitos,
  - muestra métricas (conteo original/final, intentos, validación).

## 13) Plan de iteración
### Fase 1 (MVP)
- UI mínima + conteo + reescritura con reintentos + validación por embeddings + reglas duras (números).
### Fase 2
- Tokens críticos configurables por el usuario.
- Reporte de “cambios detectados” en lenguaje natural.
### Fase 3 (opcional)
- Streaming con detención al cierre de oración y dentro del rango (solo si se justifica).
- Historial de versiones y comparación lado a lado.

## 14) Riesgos y mitigaciones
- Deriva semántica: validación semántica + reglas duras + modo estricto.
- Costos por reintentos: delta explícito + límite de intentos + targetWords.
- Textos muy cortos/largos: fallback a modo estricto, o respuesta controlada si excede límites.
- Ambigüedad en “palabra”: definición única y estable de conteo.

## 15) Preguntas abiertas (para resolver temprano)
- ¿Qué definición exacta de “palabra” se usará (guiones, números con unidades, abreviaturas)?
- ¿Se permitirá modificar puntuación/estilo libremente o se requiere conservar tono formal?
- ¿Cuál umbral de similitud es aceptable para ítems ICFES/Saber según tu experiencia?
- ¿Se requiere soporte multilenguaje (ES/EN) o solo español?

