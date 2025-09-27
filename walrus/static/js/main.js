// Main JavaScript for Walrus Repository Viewer

// Utility functions
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        // Fallback for older browsers
        fallbackCopyToClipboard(text);
    });
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showNotification('Copied to clipboard!');
        } else {
            showNotification('Failed to copy', 'error');
        }
    } catch (err) {
        console.error('Fallback: Could not copy text: ', err);
        showNotification('Failed to copy', 'error');
    }
    
    document.body.removeChild(textArea);
}

function showNotification(message, type = 'success') {
    // Remove existing notification
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Show with animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

function downloadRepository(blobId) {
    showNotification('Download functionality coming soon!', 'info');
    // TODO: Implement repository download
    // This would trigger a download of the zip file from Walrus
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    // Less than 1 minute
    if (diff < 60000) {
        return 'just now';
    }
    
    // Less than 1 hour
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    }
    
    // Less than 1 day
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }
    
    // Less than 1 week
    if (diff < 604800000) {
        const days = Math.floor(diff / 86400000);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }
    
    // Format as date
    return date.toLocaleDateString();
}

// Auto-refresh functionality
function enableAutoRefresh() {
    const refreshInterval = 30000; // 30 seconds
    
    setInterval(() => {
        // Only refresh the dashboard page
        if (window.location.pathname === '/') {
            fetch('/api/repositories')
                .then(response => response.json())
                .then(data => {
                    updateRepositoryList(data);
                })
                .catch(err => {
                    console.error('Auto-refresh failed:', err);
                });
        }
    }, refreshInterval);
}

function updateRepositoryList(repositories) {
    const container = document.querySelector('.repositories-grid');
    if (!container) return;
    
    // Simple check if data has changed (you'd want more sophisticated checking in production)
    const currentCount = container.children.length;
    if (currentCount !== repositories.length) {
        // Reload the page to get the updated layout
        window.location.reload();
    }
}

// File tree navigation
function initializeFileTree() {
    const fileItems = document.querySelectorAll('.file-item.directory');
    
    fileItems.forEach(item => {
        item.addEventListener('click', (e) => {
            // Add loading state
            const link = item.querySelector('a');
            if (link) {
                link.style.opacity = '0.6';
                link.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            }
        });
    });
}

// Keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K: Search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            // TODO: Implement search functionality
            showNotification('Search functionality coming soon!', 'info');
        }
        
        // G + H: Go home
        if (e.key === 'g') {
            document.addEventListener('keydown', function goHome(e2) {
                if (e2.key === 'h') {
                    window.location.href = '/';
                }
                document.removeEventListener('keydown', goHome);
            });
        }
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Enable auto-refresh on dashboard
    if (window.location.pathname === '/') {
        enableAutoRefresh();
    }
    
    // Initialize file tree navigation
    initializeFileTree();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Update timestamps to relative format
    document.querySelectorAll('.timestamp').forEach(element => {
        const timestamp = element.textContent;
        if (timestamp) {
            element.textContent = formatTimestamp(timestamp);
        }
    });
    
    // Format file sizes
    document.querySelectorAll('.file-size').forEach(element => {
        const sizeText = element.textContent;
        const sizeMatch = sizeText.match(/(\d+) bytes/);
        if (sizeMatch) {
            const bytes = parseInt(sizeMatch[1]);
            element.textContent = formatFileSize(bytes);
        }
    });
});

// Export functions for use in templates
window.WalrusViewer = {
    copyToClipboard,
    showNotification,
    downloadRepository,
    formatFileSize,
    formatTimestamp
};