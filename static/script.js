const form = document.getElementById('predictionForm');
const emailInput = document.getElementById('emailInput');
const submitBtn = document.getElementById('submitBtn');
const resultContainer = document.getElementById('resultContainer');
const resultContent = document.getElementById('resultContent');
const loadingSpinner = document.getElementById('loadingSpinner');
const errorContainer = document.getElementById('errorContainer');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = emailInput.value.trim();
    
    if (!message) {
        showError('Please enter an email message');
        return;
    }
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.textContent = 'Analyzing...';
    loadingSpinner.classList.remove('hidden');
    resultContent.innerHTML = '';
    errorContainer.classList.add('hidden');
    resultContainer.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Prediction failed');
        }
        
        const data = await response.json();
        displayResult(data);
        
    } catch (error) {
        showError(error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Analyze Email';
        loadingSpinner.classList.add('hidden');
    }
});

function displayResult(data) {
    const isSpam = data.prediction === 'Spam';
    const icon = isSpam ? '⚠️' : '✅';
    const className = isSpam ? 'spam' : 'ham';
    
    const html = `
        <div class="result-badge">${icon}</div>
        <div class="result-label ${className}">${data.prediction}</div>
        <p class="result-message">
            ${isSpam 
                ? 'This email appears to be spam. Be cautious and do not click suspicious links.' 
                : 'This email appears to be legitimate. It looks safe to read.'}
        </p>
        
        <div class="confidence-container">
            <div class="confidence-item">
                <div class="confidence-label">
                    <span>✅ Legitimate (Ham)</span>
                    <span>${data.ham_confidence.toFixed(1)}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill ham" style="width: ${data.ham_confidence}%"></div>
                </div>
            </div>
            
            <div class="confidence-item">
                <div class="confidence-label">
                    <span>⚠️ Spam</span>
                    <span>${data.spam_confidence.toFixed(1)}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill spam" style="width: ${data.spam_confidence}%"></div>
                </div>
            </div>
        </div>
    `;
    
    resultContent.innerHTML = html;
}

function showError(message) {
    errorContainer.textContent = '❌ ' + message;
    errorContainer.classList.remove('hidden');
    resultContainer.classList.add('hidden');
}

// Auto-resize textarea
emailInput.addEventListener('input', () => {
    emailInput.style.height = 'auto';
    emailInput.style.height = Math.min(emailInput.scrollHeight, 300) + 'px';
});
