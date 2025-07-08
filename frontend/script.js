document.addEventListener('DOMContentLoaded', () => {
    const emailContentInput = document.getElementById('emailContent');
    const fileUploadInput = document.getElementById('fileUpload');
    const submitButton = document.getElementById('submit');
    const loadingMessage = document.getElementById('loading');
    const errorMessage = document.getElementById('errorMessage');
    const resultsSection = document.getElementById('results');
    const classificationResult = document.getElementById('classificationResult');
    const suggestedResponse = document.getElementById('suggestedResponse');

    const API_BASE_URL = 'https://automail-ai-3s6l.onrender.com'; // Sua URL base do backend no Render
    const apiURL = `${API_BASE_URL}/api/classify`; // O endpoint completo para a classificação

    // Garante que todas as mensagens e a seção de resultados comecem escondidas
    hideAllMessagesAndResults(); 
    
    submitButton.addEventListener('click', handleSubmit);

    emailContentInput.addEventListener('input', () => {
        if (emailContentInput.value.trim() !== '') {
            fileUploadInput.value = '';
        }
        updateButtonState();
    });

    fileUploadInput.addEventListener('change', () => {
        if (fileUploadInput.files.length > 0) {
            emailContentInput.value = '';
        }
        updateButtonState();
    });

    function updateButtonState() {
        const hasText = emailContentInput.value.trim() !== '';
        const hasFile = fileUploadInput.files.length > 0;
        submitButton.disabled = !hasText && !hasFile;
    }

    updateButtonState();

    async function handleSubmit() {
        hideAllMessagesAndResults(); 
        showMessage(loadingMessage, 'Processando Email. Aguarde...');
        submitButton.disabled = true;

        const emailText = emailContentInput.value.trim();
        const selectedFile = fileUploadInput.files[0];

        if (!emailText && !selectedFile) {
            hideMessage(loadingMessage);
            showMessage(errorMessage, 'Por favor, digite um email ou selecione um arquivo.');
            submitButton.disabled = false;
            return;
        }

        try {
            let response;
            if (selectedFile) {
                const formData = new FormData();
                formData.append('file', selectedFile);

                response = await fetch(apiURL, { // <--- CORRIGIDO AQUI: USAR apiURL
                    method: 'POST',
                    body: formData,
                });
            } else {
                response = await fetch(apiURL, { // <--- CORRIGIDO AQUI: USAR apiURL
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email_text: emailText }),
                });
            }

            if (!response.ok) {
                // Tenta ler o erro do corpo da resposta, se disponível e JSON
                const errorText = await response.text();
                let errorData;
                try {
                    errorData = JSON.parse(errorText);
                } catch (e) {
                    errorData = { error: errorText || `Erro desconhecido: ${response.status} ${response.statusText}` };
                }
                throw new Error(errorData.error || `Erro de rede: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();

            if (data.classificacao) {
                classificationResult.textContent = data.classificacao;
                classificationResult.classList.remove('Produtivo', 'Improdutivo'); 
                // Pega apenas a primeira palavra da classificação para aplicar a classe
                const cleanedClassification = data.classificacao.trim().split(' ')[0]; 
                classificationResult.classList.add(cleanedClassification); 
            } else {
                classificationResult.textContent = "Classificação não disponível";
            }

            if (data.resposta_sugerida) {
                suggestedResponse.value = data.resposta_sugerida;
            } else {
                suggestedResponse.value = "Nenhuma resposta sugerida.";
            }

            // Exibe a seção de resultados e força visibilidade
            resultsSection.style.cssText = ''; 
            resultsSection.classList.remove('hidden');
            resultsSection.style.display = 'block';
            resultsSection.style.opacity = '1';
            resultsSection.style.visibility = 'visible';
            resultsSection.style.minHeight = '250px'; 

            classificationResult.style.cssText = ''; 
            classificationResult.style.display = 'block';
            classificationResult.style.opacity = '1';
            classificationResult.style.visibility = 'visible';

            suggestedResponse.style.cssText = ''; 
            suggestedResponse.style.display = 'block';
            suggestedResponse.style.opacity = '1';
            suggestedResponse.style.visibility = 'visible';

        } catch (error) {
            console.error('Erro:', error); // Log de erro mais conciso
            showMessage(errorMessage, error.message);
        } finally {
            hideMessage(loadingMessage);
            submitButton.disabled = false;
            updateButtonState();
        }
    }

    // Oculta um elemento e limpa estilos inline
    function hideMessage(element) {
        element.classList.add('hidden');
        element.textContent = ''; 
        element.style.cssText = ''; 
    }

    // Exibe um elemento e garante visibilidade
    function showMessage(element, text = '') {
        element.textContent = text;
        element.classList.remove('hidden');
        element.style.cssText = ''; 
        element.style.display = 'block'; 
        element.style.opacity = '1';
        element.style.visibility = 'visible';
    }

    // Oculta todas as mensagens de feedback e a seção de resultados
    function hideAllMessagesAndResults() {
        hideMessage(loadingMessage);
        hideMessage(errorMessage);

        resultsSection.classList.add('hidden');
    }
});