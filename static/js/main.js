// Main JavaScript for SOF-ELK Web Interface

document.addEventListener('DOMContentLoaded', function() {
    // Handle form submissions with confirmation
    const confirmForms = document.querySelectorAll('form[data-confirm]');
    confirmForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const confirmMessage = this.getAttribute('data-confirm');
            if (!confirm(confirmMessage)) {
                e.preventDefault();
            }
        });
    });

    // File input enhancement
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        const fileNameDisplay = document.createElement('span');
        fileNameDisplay.className = 'file-name';
        input.parentNode.appendChild(fileNameDisplay);

        input.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
            } else {
                fileNameDisplay.textContent = '';
            }
        });
    });

    // Dynamic form fields
    const logTypeSelect = document.querySelector('select[name="log_type"]');
    const yearField = document.querySelector('.form-group.year-field');
    
    if (logTypeSelect && yearField) {
        logTypeSelect.addEventListener('change', function() {
            if (this.value === 'syslog') {
                yearField.style.display = 'block';
            } else {
                yearField.style.display = 'none';
            }
        });
        
        // Trigger on page load
        if (logTypeSelect.value === 'syslog') {
            yearField.style.display = 'block';
        } else {
            yearField.style.display = 'none';
        }
    }

    // Process type select for NetFlow processing
    const processTypeSelect = document.querySelector('select[name="process_type"]');
    const exporterIpField = document.querySelector('.form-group.exporter-ip-field');
    
    if (processTypeSelect && exporterIpField) {
        processTypeSelect.addEventListener('change', function() {
            if (this.value === 'netflow') {
                exporterIpField.style.display = 'block';
            } else {
                exporterIpField.style.display = 'none';
            }
        });
        
        // Trigger on page load
        if (processTypeSelect.value === 'netflow') {
            exporterIpField.style.display = 'block';
        } else {
            exporterIpField.style.display = 'none';
        }
    }

    // Auto-dismiss messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });
});
