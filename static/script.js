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

function handleFile(file) {
    if (!file.type.startsWith('image/') && file.type !== 'application/pdf') {
        alert('Please upload an image or PDF file.');
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
    settingsPanel.classList.toggle('hidden');
}

function loadSettings() {
    const openai = localStorage.getItem('openai_key');
    const gemini = localStorage.getItem('gemini_key');
    if (openai) document.getElementById('openaiKey').value = openai;
    if (gemini) document.getElementById('geminiKey').value = gemini;
}

function saveSettings() {
    const openai = document.getElementById('openaiKey').value;
    const gemini = document.getElementById('geminiKey').value;
    localStorage.setItem('openai_key', openai);
    localStorage.setItem('gemini_key', gemini);
    toggleSettings();
}

async function processExtraction() {
    if (!currentFile) return;
    
    const provider = document.getElementById('providerSelect').value;
    const prompt = promptInput.value || "Extract all text from this image.";
    const key = provider === 'openai' ? 
        localStorage.getItem('openai_key') : 
        localStorage.getItem('gemini_key');
        
    // Allow empty key if user relies on backend .env
    
    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('prompt', prompt);
    formData.append('provider', provider);
    if (key) formData.append('api_key', key);
    
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
    alert('Copied to clipboard!');
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
        const res = await fetch(`${API_URL}/history`);
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
    // We can't restore the file object to input, but we can show the result.
    // Ideally we would support base64 preview or file serving.
    // For now, let's just show the result and prompt.
    promptInput.value = item.prompt;
    showResult(item.result);
    // Hide upload, show placeholder preview?
    // Simply jumping to result is fine.
}
