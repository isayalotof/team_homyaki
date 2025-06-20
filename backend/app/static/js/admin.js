/**
 * Admin Panel JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content');
            
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
            
            // Save state to localStorage
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
        
        // Restore sidebar state from localStorage on page load
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed) {
            document.getElementById('sidebar').classList.add('collapsed');
            document.getElementById('content').classList.add('expanded');
        }
    }
    
    // Ensure sidebar is properly visible on mobile when needed
    function checkSidebarVisibility() {
        const sidebar = document.getElementById('sidebar');
        const content = document.getElementById('content');
        if (window.innerWidth <= 768) {
            sidebar.classList.add('collapsed');
            content.classList.add('expanded');
        } else {
            // Only restore if not explicitly collapsed by user
            if (localStorage.getItem('sidebarCollapsed') !== 'true') {
                sidebar.classList.remove('collapsed');
                content.classList.remove('expanded');
            }
        }
    }
    
    // Run on page load
    checkSidebarVisibility();
    
    // Run when window is resized
    window.addEventListener('resize', checkSidebarVisibility);
    
    // Initialize dropdown toggles
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        new bootstrap.Dropdown(toggle);
    });
    
    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const previewId = this.dataset.previewId;
            if (!previewId) return;
            
            const previewElement = document.getElementById(previewId);
            if (!previewElement) return;
            
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    if (previewElement.tagName === 'IMG') {
                        previewElement.src = e.target.result;
                        previewElement.classList.remove('d-none');
                    } else {
                        const img = previewElement.querySelector('img');
                        if (img) {
                            img.src = e.target.result;
                            previewElement.classList.remove('d-none');
                        }
                    }
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    
    // Initialize all tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    // Data tables initialization
    const dataTables = document.querySelectorAll('.data-table');
    if (dataTables.length > 0 && typeof $.fn.DataTable !== 'undefined') {
        dataTables.forEach(table => {
            $(table).DataTable({
                responsive: true,
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Russian.json'
                }
            });
        });
    }
    
    // Drag & Drop for image upload
    const dropzones = document.querySelectorAll('.dropzone');
    dropzones.forEach(dropzone => {
        const fileInput = dropzone.querySelector('input[type="file"]');
        if (!fileInput) return;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropzone.classList.add('dragover');
        }
        
        function unhighlight() {
            dropzone.classList.remove('dragover');
        }
        
        dropzone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            fileInput.files = files;
            
            // Trigger change event manually
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
        
        // Click on dropzone to trigger file input
        dropzone.addEventListener('click', function() {
            fileInput.click();
        });
    });
    
    // Handle filter form submission
    const filterForms = document.querySelectorAll('[data-filter-form]');
    filterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const searchParams = new URLSearchParams();
            
            for (const [key, value] of formData.entries()) {
                if (value) {
                    searchParams.append(key, value);
                }
            }
            
            // Add page=1 to reset pagination when filtering
            searchParams.set('page', '1');
            
            // Redirect to the same page with filters
            window.location.search = searchParams.toString();
        });
    });
    
    // Handle select all checkboxes
    const selectAll = document.querySelector('[data-select-all]');
    if (selectAll) {
        const checkboxes = document.querySelectorAll(`[data-checkbox="${selectAll.dataset.selectAll}"]`);
        
        selectAll.addEventListener('change', function() {
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
        
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                // If any checkbox is unchecked, uncheck the "select all" checkbox
                if (!this.checked) {
                    selectAll.checked = false;
                }
                
                // If all checkboxes are checked, check the "select all" checkbox
                if (Array.from(checkboxes).every(cb => cb.checked)) {
                    selectAll.checked = true;
                }
            });
        });
    }
    
    // Handle bulk actions
    const bulkActionSelects = document.querySelectorAll('[data-bulk-action-select]');
    bulkActionSelects.forEach(select => {
        select.addEventListener('change', function() {
            const action = this.value;
            if (!action) return;
            
            const targetName = this.dataset.bulkActionSelect;
            const checkboxes = document.querySelectorAll(`[data-checkbox="${targetName}"]:checked`);
            
            if (checkboxes.length === 0) {
                alert('Выберите хотя бы один элемент');
                this.value = '';
                return;
            }
            
            const ids = Array.from(checkboxes).map(cb => cb.value);
            
            if (confirm(`Вы действительно хотите выполнить действие "${this.options[this.selectedIndex].text}" для выбранных элементов (${ids.length})?`)) {
                const event = new CustomEvent('bulkAction', {
                    detail: { action, ids }
                });
                this.dispatchEvent(event);
            }
            
            // Reset select
            this.value = '';
        });
    });
});

/**
 * Format number as currency
 * @param {number} value - The number to format
 * @param {string} currency - Currency symbol
 */
function formatCurrency(value, currency = '₽') {
    return new Intl.NumberFormat('ru-RU').format(value) + ' ' + currency;
}

/**
 * Format date
 * @param {string|Date} date - Date to format
 * @param {boolean} includeTime - Whether to include time
 */
function formatDate(date, includeTime = false) {
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return new Date(date).toLocaleDateString('ru-RU', options);
}

/**
 * Show notification
 * @param {string} message - Message to display
 * @param {string} type - Type of notification (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'success', duration = 3000) {
    const notificationContainer = document.getElementById('notificationContainer');
    
    if (!notificationContainer) {
        // Create container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'notificationContainer';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to container
    document.getElementById('notificationContainer').appendChild(notification);
    
    // Auto-dismiss after duration
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 150);
    }, duration);
}

/**
 * Make API request
 * @param {string} url - API endpoint
 * @param {Object} options - Fetch options
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(options.headers || {})
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка запроса');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message, 'error');
        throw error;
    }
} 