/* JavaScript para la interfaz web */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('rewriteForm');
    const inputText = document.getElementById('inputText');
    const charCount = document.getElementById('charCount');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const dismissError = document.getElementById('dismissError');

    // Contar caracteres en tiempo real
    inputText.addEventListener('input', function() {
        charCount.textContent = `${this.value.length} caracteres`;
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
