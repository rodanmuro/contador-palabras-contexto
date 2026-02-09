/* JavaScript para la interfaz web */

// Estructura de precios de modelos
const modelPricing = {
    'gpt-4o-mini': { input: 0.15, cached: 0.075, output: 0.60, name: 'GPT-4o Mini' },
    'gpt-3.5-turbo': { input: 0.50, cached: 0.25, output: 1.50, name: 'GPT-3.5 Turbo' },
    'gpt-4.1-mini': { input: 0.40, cached: 0.10, output: 1.60, name: 'GPT-4.1 Mini' },
    'gpt-4.1': { input: 2.00, cached: 0.50, output: 8.00, name: 'GPT-4.1' },
    'gpt-4o': { input: 5.00, cached: 2.50, output: 15.00, name: 'GPT-4o' }
};

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('rewriteForm');
    const inputText = document.getElementById('inputText');
    const charCount = document.getElementById('charCount');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const dismissError = document.getElementById('dismissError');

    // Contar palabras en tiempo real
    inputText.addEventListener('input', function() {
        const wordCount = this.value.trim().split(/\s+/).filter(word => word.length > 0).length;
        charCount.textContent = `${wordCount} palabras`;
    });

    // Enviar formulario
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await submitRewrite();
    });

    // Copiar texto
    copyBtn.addEventListener('click', function() {
        const finalText = document.getElementById('finalText');
        navigator.clipboard.writeText(finalText.value).then(() => {
            alert('Texto copiado al portapapeles');
        });
    });

    // Descargar reporte
    downloadBtn.addEventListener('click', async function() {
        await submitRewrite(true);  // true = descargar
    });

    // Cerrar error
    dismissError.addEventListener('click', function() {
        errorSection.classList.add('hidden');
    });

    // Función para actualizar precios cuando se cambia el modelo
    window.updateModelPricing = function() {
        const model = document.getElementById('model').value;
        const option = document.querySelector(`#model option[value="${model}"]`);
        if (option) {
            const pricing = modelPricing[model];
            console.log(`Modelo seleccionado: ${pricing.name}`);
            console.log(`Precios - Input: $${pricing.input}, Cached: $${pricing.cached}, Output: $${pricing.output}`);
        }
    };

    // Función para enviar solicitud de reescritura
    async function submitRewrite(download = false) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtn = submitBtn.textContent;
        
        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Reescribiendo...';

            const data = {
                input_text: document.getElementById('inputText').value,
                min_words: parseInt(document.getElementById('minWords').value),
                max_words: parseInt(document.getElementById('maxWords').value),
                model: document.getElementById('model').value,
                mode: document.getElementById('mode').value,
                max_attempts: parseInt(document.getElementById('maxAttempts').value)
            };

            const endpoint = download ? '/api/download' : '/api/rewrite';
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const error = await response.json();
                showError(error.error || 'Error en la solicitud');
                return;
            }

            if (download) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `reescritura_${new Date().toISOString().slice(0, 10)}.txt`;
                a.click();
                window.URL.revokeObjectURL(url);
            } else {
                const result = await response.json();
                displayResult(result);
            }
        } catch (error) {
            showError(`Error: ${error.message}`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalBtn;
        }
    }

    // Mostrar resultado
    function displayResult(result) {
        errorSection.classList.add('hidden');
        
        document.getElementById('originalCount').textContent = result.original_word_count;
        document.getElementById('finalCount').textContent = result.final_word_count;
        document.getElementById('totalAttempts').textContent = result.total_attempts;
        document.getElementById('finalText').value = result.final_text;
        document.getElementById('finalWordCount').textContent = `${result.final_word_count} palabras`;
        
        // Mostrar información de costo
        const modelName = result.model ? modelPricing[result.model]?.name : 'Desconocido';
        document.getElementById('modelUsed').textContent = modelName || result.model || '-';
        
        if (result.token_metrics) {
            const tokens = result.token_metrics;
            const totalTokens = tokens.total_tokens || 0;
            document.getElementById('tokensUsed').textContent = `${tokens.input_tokens}+${tokens.cached_tokens}(📌)+${tokens.output_tokens}=${totalTokens}`;
        } else {
            document.getElementById('tokensUsed').textContent = 'No disponible';
        }
        
        document.getElementById('estimatedCost').textContent = `$${result.total_cost_usd?.toFixed(6) || '0.00'}`;

        // Mostrar resumen
        const summary = document.getElementById('summary');
        summary.innerHTML = result.summary;
        if (result.success) {
            summary.classList.remove('error');
        } else {
            summary.classList.add('error');
        }
        summary.classList.remove('hidden');

        // Mostrar intentos
        if (result.attempts && result.attempts.length > 0) {
            displayAttempts(result.attempts);
        }

        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Mostrar detalles de intentos
    function displayAttempts(attempts) {
        const attemptsDetails = document.getElementById('attemptsDetails');
        const attemptsList = document.getElementById('attemptsList');
        attemptsList.innerHTML = '';

        attempts.forEach(attempt => {
            const item = document.createElement('div');
            item.className = `attempt-item ${attempt.status === 'ACCEPTED' ? 'accepted' : 'rejected'}`;
            
            let status = attempt.status;
            if (status === 'IN_RANGE_PENDING_VALIDATION') {
                status = 'En validación';
            } else if (status === 'OUT_OF_RANGE') {
                status = 'Fuera de rango';
            }

            let tokenInfo = '';
            if (attempt.token_metrics) {
                const tm = attempt.token_metrics;
                tokenInfo = `
                <div class="attempt-detail">
                    <span class="attempt-detail-label">Tokens:</span>
                    <span class="attempt-detail-value">${tm.input_tokens}+${tm.cached_tokens}(📌)+${tm.output_tokens}=${tm.total_tokens}</span>
                </div>
                <div class="attempt-detail">
                    <span class="attempt-detail-label">Costo:</span>
                    <span class="attempt-detail-value">$${tm.cost_usd.toFixed(6)}</span>
                </div>
                `;
            }

            item.innerHTML = `
                <div class="attempt-header">
                    <span>Intento ${attempt.attempt_number}</span>
                    <span class="attempt-status ${attempt.status}">${status}</span>
                </div>
                <div class="attempt-details">
                    <div class="attempt-detail">
                        <span class="attempt-detail-label">Palabras:</span>
                        <span class="attempt-detail-value">${attempt.word_count}</span>
                    </div>
                    ${attempt.delta !== 0 ? `
                    <div class="attempt-detail">
                        <span class="attempt-detail-label">Delta:</span>
                        <span class="attempt-detail-value">${attempt.delta > 0 ? '+' : ''}${attempt.delta}</span>
                    </div>
                    ` : ''}
                    ${tokenInfo}
                    ${attempt.similarity_score !== null ? `
                    <div class="attempt-detail">
                        <span class="attempt-detail-label">Similitud:</span>
                        <span class="attempt-detail-value">${(attempt.similarity_score * 100).toFixed(1)}%</span>
                    </div>
                    ` : ''}
                    ${attempt.error_message ? `
                    <div class="attempt-detail">
                        <span class="attempt-detail-label">Error:</span>
                        <span class="attempt-detail-value">${attempt.error_message}</span>
                    </div>
                    ` : ''}
                </div>
                <div class="attempt-text">
                    <label for="attempt_text_${attempt.attempt_number}" class="attempt-text-label">Salida del modelo:</label>
                    <textarea id="attempt_text_${attempt.attempt_number}" class="attempt-textarea" rows="4" readonly>${attempt.proposed_text || ''}</textarea>
                </div>
            `;
            attemptsList.appendChild(item);
        });

        attemptsDetails.classList.remove('hidden');
    }

    // Mostrar error
    function showError(message) {
        errorSection.classList.remove('hidden');
        document.getElementById('errorMessage').textContent = message;
        resultSection.classList.add('hidden');
    }
});
