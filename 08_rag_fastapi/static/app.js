// API Base URL
const API_BASE = '';

// DOM Elements
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const fileUpload = document.getElementById('fileUpload');
const documentsList = document.getElementById('documentsList');
const indexBtn = document.getElementById('indexBtn');
const questionInput = document.getElementById('questionInput');
const askBtn = document.getElementById('askBtn');
const chatMessages = document.getElementById('chatMessages');
const loadingOverlay = document.getElementById('loadingOverlay');

// State
let isSystemReady = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    loadDocuments();
    
    // Event Listeners
    fileUpload.addEventListener('change', handleFileUpload);
    indexBtn.addEventListener('click', handleIndexDocuments);
    askBtn.addEventListener('click', handleAskQuestion);
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleAskQuestion();
        }
    });
});

// Check System Status
async function checkStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        isSystemReady = data.documents_indexed;
        
        if (isSystemReady) {
            statusDot.classList.add('ready');
            statusDot.classList.remove('not-ready');
            statusText.textContent = '✓ Hệ thống sẵn sàng';
            askBtn.disabled = false;
        } else {
            statusDot.classList.add('not-ready');
            statusDot.classList.remove('ready');
            statusText.textContent = '⚠ Cần index documents';
            askBtn.disabled = true;
        }
    } catch (error) {
        console.error('Error checking status:', error);
        statusText.textContent = '❌ Lỗi kết nối';
    }
}

// Load Documents List
async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE}/api/documents`);
        const data = await response.json();
        
        if (data.documents.length === 0) {
            documentsList.innerHTML = '<p class="loading">Chưa có tài liệu nào</p>';
            return;
        }
        
        documentsList.innerHTML = data.documents.map(doc => `
            <div class="document-item">
                <div class="document-info">
                    <div class="document-name">📄 ${doc.filename}</div>
                    <div class="document-size">${doc.size_mb} MB</div>
                </div>
                <button class="delete-btn" onclick="deleteDocument('${doc.filename}')">
                    🗑️
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading documents:', error);
        documentsList.innerHTML = '<p class="error">Lỗi tải danh sách</p>';
    }
}

// Handle File Upload
async function handleFileUpload(event) {
    const files = event.target.files;
    if (!files.length) return;
    
    showLoading(true);
    
    for (const file of files) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${API_BASE}/api/upload`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showNotification(`✓ Upload thành công: ${file.name}`, 'success');
            } else {
                showNotification(`✗ Lỗi upload: ${data.detail}`, 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showNotification(`✗ Lỗi upload: ${file.name}`, 'error');
        }
    }
    
    // Reset input and reload documents
    fileUpload.value = '';
    await loadDocuments();
    showLoading(false);
}

// Delete Document
async function deleteDocument(filename) {
    if (!confirm(`Xóa tài liệu "${filename}"?`)) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/documents/${filename}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('✓ Đã xóa tài liệu', 'success');
            await loadDocuments();
            await checkStatus();
        } else {
            showNotification('✗ Lỗi xóa tài liệu', 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showNotification('✗ Lỗi xóa tài liệu', 'error');
    }
}

// Handle Index Documents
async function handleIndexDocuments() {
    if (!confirm('Index tất cả documents? Quá trình này có thể mất vài phút.')) return;
    
    showLoading(true);
    indexBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/api/index`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            showNotification(`✓ ${data.message}`, 'success');
            await checkStatus();
        } else {
            showNotification(`✗ ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Index error:', error);
        showNotification('✗ Lỗi khi index documents', 'error');
    } finally {
        showLoading(false);
        indexBtn.disabled = false;
    }
}

// Handle Ask Question
async function handleAskQuestion() {
    const question = questionInput.value.trim();
    
    if (!question) {
        showNotification('⚠ Vui lòng nhập câu hỏi', 'warning');
        return;
    }
    
    if (!isSystemReady) {
        showNotification('⚠ Hệ thống chưa sẵn sàng. Hãy index documents trước!', 'warning');
        return;
    }
    
    // Add user message to chat
    addMessage('user', question);
    
    // Clear input
    questionInput.value = '';
    
    // Show loading
    askBtn.disabled = true;
    askBtn.textContent = 'Đang xử lý...';
    
    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        if (data.error) {
            addMessage('assistant', `❌ Lỗi: ${data.error}`, []);
        } else {
            addMessage('assistant', data.answer, data.sources);
        }
    } catch (error) {
        console.error('Query error:', error);
        addMessage('assistant', '❌ Lỗi khi xử lý câu hỏi. Vui lòng thử lại.', []);
    } finally {
        askBtn.disabled = false;
        askBtn.textContent = 'Gửi 🚀';
    }
}

// Add Message to Chat
function addMessage(role, content, sources = []) {
    // Remove welcome message if exists
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    let messageHTML = `
        <div class="message-header">
            ${role === 'user' ? '👤 Bạn' : '🤖 AI Assistant'}
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    // Add sources if available
    if (sources && sources.length > 0) {
        messageHTML += `
            <div class="sources">
                <div class="sources-title">📚 Nguồn tham khảo:</div>
                ${sources.map((source, idx) => `
                    <div class="source-item">
                        <div class="source-content">${escapeHtml(source.content)}</div>
                        <div class="source-metadata">
                            Page: ${source.metadata.page || 'N/A'} | 
                            Source: ${source.metadata.source || 'N/A'}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    messageDiv.innerHTML = messageHTML;
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show/Hide Loading Overlay
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

// Show Notification
function showNotification(message, type = 'info') {
    // Simple console notification (you can enhance this with a toast library)
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Visual feedback in status
    const originalText = statusText.textContent;
    statusText.textContent = message;
    
    setTimeout(() => {
        checkStatus();
    }, 3000);
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-refresh status every 30 seconds
setInterval(checkStatus, 30000);