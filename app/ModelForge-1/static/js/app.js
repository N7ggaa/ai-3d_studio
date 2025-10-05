// Global application JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // File upload drag and drop functionality
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        const parent = input.closest('.form-group') || input.parentElement;
        
        // Add drag and drop styling
        parent.addEventListener('dragover', function(e) {
            e.preventDefault();
            parent.classList.add('drag-over');
        });
        
        parent.addEventListener('dragleave', function(e) {
            e.preventDefault();
            parent.classList.remove('drag-over');
        });
        
        parent.addEventListener('drop', function(e) {
            e.preventDefault();
            parent.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                input.dispatchEvent(event);
            }
        });
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Progress tracking for long-running operations
    window.trackJobProgress = function(jobId) {
        const progressModal = document.getElementById('progressModal');
        const progressBar = document.querySelector('#progressModal .progress-bar');
        const progressText = document.querySelector('#progressModal .progress-text');
        
        if (!progressModal) return;
        
        const modal = new bootstrap.Modal(progressModal);
        modal.show();
        
        const checkStatus = function() {
            fetch(`/api/job_status/${jobId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'completed') {
                        progressBar.style.width = '100%';
                        progressText.textContent = 'Generation completed!';
                        setTimeout(() => {
                            modal.hide();
                            window.location.href = `/download/${jobId}`;
                        }, 1000);
                    } else if (data.status === 'failed') {
                        progressBar.classList.add('bg-danger');
                        progressText.textContent = 'Generation failed';
                        setTimeout(() => modal.hide(), 2000);
                    } else if (data.status === 'processing') {
                        progressBar.style.width = '50%';
                        progressText.textContent = 'Generating 3D model...';
                        setTimeout(checkStatus, 3000);
                    } else {
                        progressBar.style.width = '25%';
                        progressText.textContent = 'Initializing...';
                        setTimeout(checkStatus, 2000);
                    }
                })
                .catch(error => {
                    console.error('Error checking job status:', error);
                    progressBar.classList.add('bg-danger');
                    progressText.textContent = 'Error checking status';
                    setTimeout(() => modal.hide(), 2000);
                });
        };
        
        checkStatus();
    };

    // Utility function to format file sizes
    window.formatFileSize = function(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Copy to clipboard functionality
    window.copyToClipboard = function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                showToast('Copied to clipboard!', 'success');
            }).catch(function(err) {
                console.error('Failed to copy text: ', err);
                showToast('Failed to copy text', 'error');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                showToast('Copied to clipboard!', 'success');
            } catch (err) {
                console.error('Failed to copy text: ', err);
                showToast('Failed to copy text', 'error');
            }
            
            document.body.removeChild(textArea);
        }
    };

    // Simple toast notification system
    window.showToast = function(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') || createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    };

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    }
});

// Re-initialize Feather icons after dynamic content changes
window.refreshFeatherIcons = function() {
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
};

// Global error handler for AJAX requests
window.handleAjaxError = function(xhr, status, error) {
    console.error('AJAX Error:', status, error);
    
    let message = 'An error occurred while processing your request.';
    
    if (xhr.responseJSON && xhr.responseJSON.error) {
        message = xhr.responseJSON.error;
    } else if (xhr.status === 404) {
        message = 'The requested resource was not found.';
    } else if (xhr.status === 500) {
        message = 'Internal server error. Please try again later.';
    } else if (xhr.status === 0) {
        message = 'Network error. Please check your connection.';
    }
    
    showToast(message, 'error');
};
