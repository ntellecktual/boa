$(document).ready(function () {
  // --- Badge Toggle ---
  $(".badge-pill").click(function () {
    $(this).siblings(".details").slideToggle();
  });

  // --- Console Log on Load ---
  console.log('Page loaded');

  // --- Scrolling Images Animation ---
  $('.scrolling-image-wrapper').each(function () {
    var $this = $(this);
    // Note: Applying animation via CSS might be cleaner if duration is constant
    $this.css('animation', 'scroll-images 10s linear infinite');
  });

  // --- Theme Toggle Logic ---
  const toggleBtn = document.getElementById("theme-toggle-btn");
  const overlay = document.getElementById("theme-transition-overlay");
  const htmlElement = document.documentElement; // Target the <html> element

  /**
   * Applies the selected theme to the document and saves it to localStorage.
   * @param {string} theme - The theme to apply ('light' or 'dark').
   * @param {boolean} isInitialLoad - True if this is the first load, false otherwise (prevents flash on load).
   */
  function applyTheme(theme, isInitialLoad = false) {
    htmlElement.setAttribute("data-theme", theme); // Set on <html> for CSS variable overrides
    document.body.setAttribute("data-theme", theme); // Also set on <body> for the ::before overlay selector
    localStorage.setItem("theme", theme);

    // Update button text/icon (using Font Awesome icons from base_generic.html)
    if (toggleBtn) {
      if (theme === "dark") {
        toggleBtn.innerHTML = '<i class="fas fa-sun"></i> Light Mode'; // Sun icon
      } else {
        toggleBtn.innerHTML = '<i class="fas fa-moon"></i> Dark Mode'; // Moon icon
      }
      // Remove rotation class after transition (or immediately if initial load)
      if (!isInitialLoad) {
        setTimeout(() => toggleBtn.classList.remove("rotating"), 400); // Match transition duration
      } else {
        toggleBtn.classList.remove("rotating");
      }
    }

    // Trigger flash animation only on toggle, not initial load
    if (overlay && !isInitialLoad) {
      const flashClass = theme === "light" ? "flash-light" : "flash-dark";
      console.log(`Applying flash for theme: ${theme}, Class: ${flashClass}`); // Debug log

      overlay.classList.remove("flash-dark", "flash-light");
      // Ensure removal happens before adding the new class
      requestAnimationFrame(() => { // Use requestAnimationFrame for better timing
        overlay.classList.add(flashClass);
        overlay.style.opacity = "1";
        setTimeout(() => { overlay.style.opacity = "0"; }, 400); // Match CSS transition
      });
    }
  }

  function toggleTheme() {
    const currentTheme = htmlElement.getAttribute("data-theme") || "light";
    const newTheme = currentTheme === "light" ? "dark" : "light";
    if (toggleBtn) { toggleBtn.classList.add("rotating"); }
    applyTheme(newTheme, false); // Apply theme with flash animation
  }

  const preferredTheme = localStorage.getItem("theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  applyTheme(preferredTheme, true); // Apply initial theme without flash

  if (toggleBtn) { toggleBtn.addEventListener("click", toggleTheme); }
  else { console.error("Theme toggle button with ID 'theme-toggle-btn' not found!"); }
  // --- End Theme Toggle Logic ---

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
      } else if (progressBar) { // Ensure progressBar exists before redirecting
        // Delay for a moment before redirecting
        setTimeout(() => {
          window.location.href = "/upload/success/";
        }, 2000); // 2 seconds for user to see 100% completion
      }
    })
    .catch(error => {
      console.error("Error updating progress:", error);
      // Optionally, re-enable button or show error message to user here
    });
}

// --- Accordion specific to uploadit.html (uploadInfoAccordion) ---
const accordion = document.getElementById("uploadInfoAccordion");
if (accordion) { // Check if the accordion element exists on the current page
  accordion.addEventListener("click", function (e) {
    const btn = e.target.closest("[data-toggle='collapse']");
    if (!btn) return;

    const targetId = btn.getAttribute("data-target");
    const target = document.querySelector(targetId);

    // Check if target exists and is shown before trying to hide
    if (target && target.classList.contains("show")) {
      $(target).collapse("hide");
      // e.stopImmediatePropagation(); // Consider if this is truly needed
    }
  });
}
// --- End Accordion specific to uploadit.html ---