document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    const uploadForm = document.getElementById('uploadForm');
    const loading = document.getElementById('loading');
    const message = document.getElementById('message');
    const mapSection = document.getElementById('mapSection');
    const mapFrame = document.getElementById('mapFrame');
    const avgSalesValue = document.getElementById('avgSalesValue');
    const submitBtn = document.getElementById('submitBtn');

    // Handle file selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileName.textContent = e.target.files[0].name;
            fileName.style.color = '#e2e8f0';
            fileName.style.borderColor = '#3b82f6';
        } else {
            fileName.textContent = 'No file chosen';
            fileName.style.color = '';
            fileName.style.borderColor = '';
        }
    });

    // Handle form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            showMessage('Please select a file first.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        // UI Transition to Loading State
        message.classList.add('hidden');
        mapSection.classList.add('hidden');
        loading.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';

        try {
            const response = await fetch('/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                showMessage(`Error: ${data.error}`, 'error');
            } else if (data.success) {
                // Formatting average sales as currency
                const formattedAvg = new Intl.NumberFormat('en-IN', {
                    style: 'currency',
                    currency: 'INR'
                }).format(data.avg_sales);

                avgSalesValue.textContent = formattedAvg;

                // Add a cache-buster query string so iframe reloads new map
                mapFrame.src = `/map?t=${new Date().getTime()}`;

                // Wait for iframe to load before showing it smoothly
                mapFrame.onload = () => {
                    loading.classList.add('hidden');
                    mapSection.classList.remove('hidden');

                    // Smooth scroll to map
                    mapSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                };
            }
        } catch (error) {
            showMessage('An error occurred while uploading. Please check network and try again.', 'error');
            console.error('Upload Error:', error);
            loading.classList.add('hidden');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generate Map';
        }
    });

    // Helper to show messages to the user
    function showMessage(msg, type) {
        message.textContent = msg;
        message.className = type;
        message.classList.remove('hidden');
    }
});
