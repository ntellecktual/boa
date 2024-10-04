$(document).ready(function () {
    $(".badge-pill").click(function () {
        $(this).siblings(".details").slideToggle();
    });
});
// Example custom JS for interactivity
$(document).ready(function () {
    console.log('Page loaded');
});

$(document).ready(function () {
    $('.scrolling-image-wrapper').each(function () {
        var $this = $(this);
        var width = $this.width();
        $this.css('animation', 'scroll-images 10s linear infinite');
    });
});

function updateProgress() {
    const fileName = document.getElementById('file_name').value;
    fetch(`/upload/progress/${encodeURIComponent(fileName)}/`)
        .then(response => response.json())
        .then(data => {
            const progressBar = document.querySelector(".progress-bar");
            progressBar.style.width = data.progress + "%";
            progressBar.innerHTML = data.progress + "%";

            // If progress is less than 100, continue polling
            if (data.progress < 100) {
                setTimeout(updateProgress, 1000);
            } else {
                // Delay for a moment before redirecting
                setTimeout(() => {
                    window.location.href = "/upload/success/";
                }, 2000); // 2 seconds for user to see 100% completion
            }
        })
        .catch(error => console.error("Error updating progress:", error));
}