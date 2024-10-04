document.addEventListener('DOMContentLoaded', function() {
    const fileName = "{{ file_name }}";
    const body = document.body;
    const csrfToken = "{{ csrf_token }}"; // Ensure the CSRF token is available

    function updateProgress() {
        fetch(uploadProgressUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `file_name=${encodeURIComponent(fileName)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.progress !== undefined && data.progress >= 100) {
                body.style.transition = "background 2.5s";
                body.style.background = "linear-gradient(to right, lightgreen, emerald)";
                setTimeout(() => {
                    body.style.background = "linear-gradient(to right, #8e2de2, #2e2443)";
                }, 2500);
            } else {
                setTimeout(updateProgress, 1000);
            }
        });
    }

    updateProgress();
});
