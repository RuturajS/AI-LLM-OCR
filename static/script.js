const API_URL = '/api';

// DOM Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const previewSection = document.getElementById('previewSection');
const resultSection = document.getElementById('resultSection');
const imagePreview = document.getElementById('imagePreview');
const fileInfo = document.getElementById('fileInfo');
const promptInput = document.getElementById('promptInput');
const settingsPanel = document.getElementById('settingsPanel');
const creditsPanel = document.getElementById('creditsPanel');
const historyList = document.getElementById('historyList');
const extractBtn = document.getElementById('extractBtn');
const resultContent = document.getElementById('resultContent');

let currentFile = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    loadHistory();

    // Dropzone Events
    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--accent)';
    });
    dropzone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--border)';
    });
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--border)';
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });
});

// Toast System
function showToast(message, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-check-circle';
    if (type === 'error') icon = 'fa-exclamation-circle';

    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;

    container.appendChild(toast);

    // Remove after 3s
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function handleFile(file) {
    if (!file.type.startsWith('image/') && file.type !== 'application/pdf') {
        showToast('Please upload an image or PDF file.', 'error');
        return;
    }

    currentFile = file;
    fileInfo.textContent = `${file.name} (${(file.size / 1024).toFixed(2)} KB)`;

    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            showPreview();
        };
        reader.readAsDataURL(file);
    } else {
        // PDF Preview Placeholder
        imagePreview.src = 'https://upload.wikimedia.org/wikipedia/commons/8/87/PDF_file_icon.svg';
        showPreview();
    }
}

function showPreview() {
    document.getElementById('uploadSection').classList.add('hidden'); // Optional: hide upload to focus
    // Actually typically we want to keep upload accessible or restart.
    // For now let's just show preview below or swap.
    document.getElementById('uploadSection').style.display = 'none';
    previewSection.classList.remove('hidden');
    resultSection.classList.add('hidden');
}

function resetApp() {
    currentFile = null;
    fileInput.value = '';
    document.getElementById('uploadSection').style.display = 'block';
    previewSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    promptInput.value = '';
}

function toggleSettings() {
    if (!creditsPanel.classList.contains('hidden')) creditsPanel.classList.add('hidden');
    settingsPanel.classList.toggle('hidden');
}

function toggleCredits() {
    if (!settingsPanel.classList.contains('hidden')) settingsPanel.classList.add('hidden');
    creditsPanel.classList.toggle('hidden');
}

function loadSettings() {
    const openai = localStorage.getItem('openai_key');
    const gemini = localStorage.getItem('gemini_key');
    const openrouter = localStorage.getItem('openrouter_key');
    if (openai) document.getElementById('openaiKey').value = openai;
    if (gemini) document.getElementById('geminiKey').value = gemini;
    if (openrouter) document.getElementById('openrouterKey').value = openrouter;

    const sys = localStorage.getItem('system_prompt');
    const temp = localStorage.getItem('temperature');
    const tokens = localStorage.getItem('max_tokens');

    if (sys) document.getElementById('systemPrompt').value = sys;
    if (temp) document.getElementById('temperature').value = temp;
    if (tokens) document.getElementById('maxTokens').value = tokens;
}

function saveSettings() {
    const openai = document.getElementById('openaiKey').value;
    const gemini = document.getElementById('geminiKey').value;
    const openrouter = document.getElementById('openrouterKey').value;

    const sys = document.getElementById('systemPrompt').value;
    const temp = document.getElementById('temperature').value;
    const tokens = document.getElementById('maxTokens').value;

    localStorage.setItem('openai_key', openai);
    localStorage.setItem('gemini_key', gemini);
    localStorage.setItem('openrouter_key', openrouter);

    localStorage.setItem('system_prompt', sys);
    localStorage.setItem('temperature', temp);
    localStorage.setItem('max_tokens', tokens);
    toggleSettings();
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('collapsed');
}

async function clearHistory() {
    if (!confirm("Are you sure you want to clear all history?")) return;

    try {
        await fetch(`${API_URL}/history`, { method: 'DELETE' });
        // Force header update or just reload manually
        historyList.innerHTML = '';
        loadHistory();
        showToast("History cleared successfully", "success");
    } catch (e) {
        showToast("Failed to clear history", "error");
    }
}

async function processExtraction() {
    if (!currentFile) return;

    const provider = document.getElementById('providerSelect').value;
    const prompt = promptInput.value || "Extract all text from this image.";
    let key = '';
    if (provider === 'openai') key = document.getElementById('openaiKey').value;
    else if (provider === 'gemini') key = document.getElementById('geminiKey').value;
    else if (provider === 'openrouter') key = document.getElementById('openrouterKey').value;

    // Allow empty key if user relies on backend .env

    const customModel = document.getElementById('customModelInput').value;

    // Get Advanced Params
    const sys = document.getElementById('systemPrompt').value;
    const temp = document.getElementById('temperature').value;
    const tokens = document.getElementById('maxTokens').value;

    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('prompt', prompt);
    formData.append('provider', provider);
    if (key) formData.append('api_key', key);
    if (customModel) formData.append('model', customModel);

    if (sys) formData.append('system_prompt', sys);
    if (temp) formData.append('temperature', temp);
    if (tokens) formData.append('max_tokens', tokens);

    setLoading(true);

    try {
        const res = await fetch(`${API_URL}/extract`, {
            method: 'POST',
            body: formData
        });

        const data = await res.json();

        if (res.ok) {
            showResult(data.result);
            loadHistory(); // Refresh history
        } else {
            showResult(`Error: ${data.error}`);
        }
    } catch (e) {
        showResult(`Network Error: ${e.message}`);
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    if (isLoading) {
        extractBtn.disabled = true;
        extractBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
    } else {
        extractBtn.disabled = false;
        extractBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Extract Text';
    }
}

function showResult(text) {
    resultSection.classList.remove('hidden');
    // Sanitize or just rely on marked
    resultContent.innerHTML = marked.parse(text);
    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

function copyResult() {
    const text = resultContent.innerText;
    navigator.clipboard.writeText(text);
    showToast('Copied to clipboard!', 'success');
}

function downloadResult() {
    const text = resultContent.innerText;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'extraction-result.txt';
    a.click();
}

async function loadHistory() {
    try {
        // Prevent cache
        const res = await fetch(`${API_URL}/history?t=${new Date().getTime()}`);
        const history = await res.json();

        historyList.innerHTML = '';
        history.forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = `
                <div style="font-weight: 600;">${item.filename}</div>
                <div style="font-size: 0.8rem; opacity: 0.7;">${new Date(item.timestamp).toLocaleTimeString()}</div>
            `;
            div.onclick = () => loadHistoryItem(item);
            historyList.appendChild(div);
        });
    } catch (e) {
        console.error('Failed to load history', e);
    }
}

function loadHistoryItem(item) {
    promptInput.value = item.prompt;
    showResult(item.result);

    // If image exists, show it
    if (item.image_path) {
        document.getElementById('uploadSection').style.display = 'none';
        previewSection.classList.remove('hidden');
        imagePreview.src = item.image_path;
        fileInfo.textContent = item.filename || "History Image";
    }
}
