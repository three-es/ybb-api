document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('apiForm');
    const submitBtn = document.getElementById('submitBtn');
    const spinner = submitBtn.querySelector('.spinner-border');
    const responseContent = document.getElementById('responseContent');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Show loading state
        submitBtn.disabled = true;
        spinner.classList.remove('d-none');
        
        // Gather form data
        const formData = {
            name: document.getElementById('name').value,
            dedication: document.getElementById('dedication').value,
            date: document.getElementById('date').value
        };

        try {
            const response = await fetch('/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            console.log('Response received:', data);
            
            // Display the raw response data
            responseContent.textContent = JSON.stringify(data, null, 2);
            responseContent.parentElement.className = 
                response.ok ? 'border rounded p-3 ' : 'border rounded p-3 bg-danger-subtle';

        } catch (error) {
            responseContent.textContent = JSON.stringify({
                success: false,
                error: 'Network error occurred'
            }, null, 2);
            responseContent.parentElement.className = 'border rounded p-3 bg-danger-subtle';
        } finally {
            // Reset loading state
            submitBtn.disabled = false;
            spinner.classList.add('d-none');
        }
    });
});
