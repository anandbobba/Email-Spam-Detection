/**
 * Spam Intelligence — Client-Side Logic
 * Real-time threat gauge + Full analysis result renderer
 */

// ─── DOM References ───────────────────────────────────────────────────────────
const messageInput  = document.getElementById('message-input');
const analyzeBtn    = document.getElementById('analyze-btn');
const clearBtn      = document.getElementById('clear-btn');
const charCount     = document.getElementById('char-count');
const langDetect    = document.getElementById('lang-detect');
const emptyState    = document.getElementById('empty-state');
const resultCard    = document.getElementById('result-card');
const statusDot     = document.getElementById('status-dot');
const statusText    = document.getElementById('status-text');

// Gauge elements
const gaugeFill  = document.getElementById('gauge-fill');
const gaugeValue = document.getElementById('gauge-value');

// Result elements
const verdictBanner  = document.getElementById('verdict-banner');
const verdictIcon    = document.getElementById('verdict-icon');
const verdictLabel   = document.getElementById('verdict-label');
const verdictSub     = document.getElementById('verdict-sub');
const verdictBadge   = document.getElementById('verdict-badge');
const metaLang       = document.getElementById('meta-lang');
const metaEngine     = document.getElementById('meta-engine');
const metaConf       = document.getElementById('meta-conf');
const phishingAlert  = document.getElementById('phishing-alert');
const phishingLinks  = document.getElementById('phishing-links');
const threatGrid     = document.getElementById('threat-grid');
const keywordSection = document.getElementById('keyword-section');
const keywordWrap    = document.getElementById('keyword-wrap');

// ─── Constants ───────────────────────────────────────────────────────────────
const GAUGE_CIRCUMFERENCE = 251; // Arc length of the semicircle (π × r = π × 80 ≈ 251)
const DEBOUNCE_DELAY = 450; // ms
let debounceTimer = null;

// ─── Gauge Animation ─────────────────────────────────────────────────────────
function setGauge(score) {
    const pct    = Math.min(Math.max(score, 0), 100);
    const offset = GAUGE_CIRCUMFERENCE - (pct / 100) * GAUGE_CIRCUMFERENCE;
    gaugeFill.style.strokeDashoffset = offset.toFixed(1);
    gaugeValue.textContent = `${Math.round(pct)}%`;

    // Color transition via stroke
    if (pct < 35)       gaugeFill.setAttribute('stroke', '#10b981');
    else if (pct < 60)  gaugeFill.setAttribute('stroke', '#f59e0b');
    else                gaugeFill.setAttribute('stroke', '#ef4444');
}

// ─── Server Ping ─────────────────────────────────────────────────────────────
async function pingServer() {
    try {
        const res = await fetch('/api/quick-score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'ping' })
        });
        if (res.ok) {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'System Online';
        } else { throw new Error(); }
    } catch {
        statusDot.className = 'status-dot error';
        statusText.textContent = 'Server Offline';
    }
}

// ─── Real-Time Quick Score ────────────────────────────────────────────────────
async function fetchQuickScore(text) {
    if (!text || text.length < 4) { setGauge(0); return; }
    try {
        const res = await fetch('/api/quick-score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        setGauge(data.score || 0);
    } catch { /* Silent fail for real-time */ }
}

// ─── Full Analysis Render ────────────────────────────────────────────────────
function renderResult(data) {
    emptyState.classList.add('hidden');
    resultCard.classList.remove('hidden');

    const isSpam = data.prediction === 'Spam';

    // Verdict Banner
    verdictBanner.style.borderBottom = `1px solid ${isSpam ? 'hsl(0,70%,58%,0.3)' : 'hsl(158,64%,42%,0.3)'}`;

    verdictIcon.className = `verdict-icon ${isSpam ? 'spam' : 'legit'}`;
    verdictIcon.innerHTML = isSpam
        ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`
        : `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`;

    verdictLabel.textContent = isSpam ? 'Spam Detected' : 'Message Appears Legitimate';
    verdictSub.textContent   = isSpam
        ? 'This message contains patterns consistent with spam or phishing.'
        : 'No significant threat indicators were found in this message.';

    verdictBadge.textContent = isSpam ? 'High Risk' : 'Low Risk';
    verdictBadge.className   = `verdict-badge ${isSpam ? 'spam' : 'legit'}`;

    // Meta
    metaLang.textContent   = data.language || '—';
    metaEngine.textContent = data.source === 'ml' ? 'SVM Model' : 'Rule Engine';
    metaConf.textContent   = `${Math.round(data.confidence)}%`;

    // Gauge sync
    setGauge(data.confidence);

    // Phishing Alert
    if (data.suspicious_links && data.suspicious_links.length > 0) {
        phishingAlert.classList.remove('hidden');
        phishingLinks.innerHTML = data.suspicious_links
            .map(l => `<div class="link-item">${escapeHtml(l)}</div>`).join('');
    } else {
        phishingAlert.classList.add('hidden');
    }

    // Threat Breakdown
    threatGrid.innerHTML = '';
    const categoryOrder = ['financial', 'urgency', 'phishing', 'social'];
    categoryOrder.forEach(key => {
        const cat = (data.threats || {})[key];
        const label = { financial: 'Financial', urgency: 'Urgency', phishing: 'Phishing', social: 'Social Eng.' }[key];
        const score = cat ? cat.score : 0;
        const maxScore = { financial: 30, urgency: 25, phishing: 35, social: 20 }[key];
        const barWidth = Math.min((score / maxScore) * 100, 100);

        threatGrid.innerHTML += `
            <div class="threat-card ${score > 0 ? 'active' : ''}">
                <div class="threat-name">${label}</div>
                <div class="threat-bar">
                    <div class="threat-bar-fill ${key}" style="width: ${barWidth}%"></div>
                </div>
                <div class="threat-score">${score > 0 ? `Score: ${score}` : 'Not detected'}</div>
            </div>`;
    });

    // Keywords
    const kws = data.keywords || [];
    if (kws.length > 0) {
        keywordSection.classList.remove('hidden');
        keywordWrap.innerHTML = kws.map(k => `<span class="kw-tag">${escapeHtml(k)}</span>`).join('');
    } else {
        keywordSection.classList.add('hidden');
    }
}

// ─── Full Analysis Fetch ──────────────────────────────────────────────────────
async function runFullAnalysis() {
    const text = messageInput.value.trim();
    if (!text) return;

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg> Analyzing...`;

    try {
        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        if (res.ok) {
            renderResult(data);
        } else {
            alert(data.error || 'Analysis failed. Please try again.');
        }
    } catch (err) {
        alert('Cannot connect to the analysis server.\nMake sure Flask is running on http://127.0.0.1:5000');
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg> Run Full Analysis`;
    }
}

// ─── Utility ─────────────────────────────────────────────────────────────────
function escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ─── Event Listeners ──────────────────────────────────────────────────────────
messageInput.addEventListener('input', () => {
    const text = messageInput.value;
    charCount.textContent = `${text.length} characters`;

    // Debounce quick score
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => fetchQuickScore(text), DEBOUNCE_DELAY);
});

analyzeBtn.addEventListener('click', runFullAnalysis);

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) runFullAnalysis();
});

clearBtn.addEventListener('click', () => {
    messageInput.value = '';
    charCount.textContent = '0 characters';
    langDetect.textContent = '';
    langDetect.classList.remove('visible');
    setGauge(0);
    emptyState.classList.remove('hidden');
    resultCard.classList.add('hidden');
});

// ─── Spinner style ────────────────────────────────────────────────────────────
const style = document.createElement('style');
style.textContent = `@keyframes spin { to { transform: rotate(360deg); } } .spin { animation: spin 0.8s linear infinite; }`;
document.head.appendChild(style);

// ─── Init ─────────────────────────────────────────────────────────────────────
pingServer();
