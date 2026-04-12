document.addEventListener('DOMContentLoaded', function () {

  // --- Badge Toggle (vanilla JS) ---
  document.querySelectorAll('.badge-pill').forEach(function (badge) {
    badge.addEventListener('click', function () {
      const details = this.parentElement.querySelector('.details');
      if (details) {
        details.style.display = details.style.display === 'none' ? 'block' : 'none';
      }
    });
  });

  // --- Scrolling Images Animation ---
  document.querySelectorAll('.scrolling-image-wrapper').forEach(function (el) {
    el.style.animation = 'scroll-images 10s linear infinite';
  });

  // --- Theme Toggle Logic ---
  const toggleBtn = document.getElementById('theme-toggle-btn');
  const overlay = document.getElementById('theme-transition-overlay');
  const htmlElement = document.documentElement;

  function applyTheme(theme, isInitialLoad) {
    htmlElement.setAttribute('data-theme', theme);
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);

    if (toggleBtn) {
      toggleBtn.innerHTML = theme === 'dark'
        ? '<i class="fas fa-sun"></i> Light Mode'
        : '<i class="fas fa-moon"></i> Dark Mode';
      if (!isInitialLoad) {
        setTimeout(function () { toggleBtn.classList.remove('rotating'); }, 400);
      } else {
        toggleBtn.classList.remove('rotating');
      }
    }

    if (overlay && !isInitialLoad) {
      var flashClass = theme === 'light' ? 'flash-light' : 'flash-dark';
      overlay.classList.remove('flash-dark', 'flash-light');
      requestAnimationFrame(function () {
        overlay.classList.add(flashClass);
        overlay.style.opacity = '1';
        setTimeout(function () { overlay.style.opacity = '0'; }, 400);
      });
    }
  }

  function toggleTheme() {
    var currentTheme = htmlElement.getAttribute('data-theme') || 'light';
    var newTheme = currentTheme === 'light' ? 'dark' : 'light';
    if (toggleBtn) { toggleBtn.classList.add('rotating'); }
    applyTheme(newTheme, false);
  }

  var preferredTheme = localStorage.getItem('theme') ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(preferredTheme, true);

  if (toggleBtn) { toggleBtn.addEventListener('click', toggleTheme); }

  // --- Accordion Deep Linking (Bootstrap 5) ---
  var urlParams = new URLSearchParams(window.location.search);
  var openAccordionId = urlParams.get('open');

  if (openAccordionId) {
    var targetPanel = document.getElementById(openAccordionId);
    if (targetPanel && targetPanel.classList.contains('collapse')) {
      var collapseInstance = new bootstrap.Collapse(targetPanel, { toggle: false });
      collapseInstance.show();

      var headerId = targetPanel.getAttribute('aria-labelledby');
      if (headerId) {
        var headerEl = document.getElementById(headerId);
        if (headerEl) {
          setTimeout(function () {
            headerEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 350);
        }
      }
    }
  }

  // --- Navbar Scroll Effect ---
  var navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    }, { passive: true });
  }

  // --- Scroll Animations (IntersectionObserver) ---
  var animatedElements = document.querySelectorAll('.fade-in-up');
  if (animatedElements.length > 0 && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          // Animate company cards
          if (entry.target.classList.contains('company-card')) {
            entry.target.classList.add('animate-in');
          }
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    animatedElements.forEach(function (el) {
      observer.observe(el);
    });
  }

  // --- Company Card Expand Icon Rotation ---
  document.querySelectorAll('.company-card-header[data-bs-toggle="collapse"]').forEach(function (header) {
    var targetId = header.getAttribute('data-bs-target');
    var target = document.querySelector(targetId);
    if (target) {
      target.addEventListener('show.bs.collapse', function () {
        header.querySelector('.expand-icon')?.classList.add('rotated');
      });
      target.addEventListener('hide.bs.collapse', function () {
        header.querySelector('.expand-icon')?.classList.remove('rotated');
      });
    }
  });

});

// --- Portfolio two-pane nav (event delegation — works for static and panel-injected content) ---
document.addEventListener('click', function (e) {
  var btn = e.target.closest('.pf-nav-item');
  if (!btn) return;
  var split = btn.closest('.pf-split') || document;
  split.querySelectorAll('.pf-nav-item').forEach(function (b) {
    b.classList.remove('pf-active');
  });
  split.querySelectorAll('.pf-panel').forEach(function (p) {
    p.style.display = 'none';
  });
  btn.classList.add('pf-active');
  var target = split.querySelector('#' + btn.dataset.target);
  if (target) { target.style.display = ''; }
});

// --- Upload Progress ---
function updateProgress() {
  var fileName = document.getElementById('file_name').value;
  fetch('/upload/progress/' + encodeURIComponent(fileName) + '/')
    .then(function (response) { return response.json(); })
    .then(function (data) {
      var progressBar = document.querySelector('.progress-bar');
      progressBar.style.width = data.progress + '%';
      progressBar.innerHTML = data.progress + '%';

      if (data.progress < 100) {
        setTimeout(updateProgress, 1000);
      } else if (progressBar) {
        setTimeout(function () {
          window.location.href = '/upload/success/';
        }, 2000);
      }
    })
    .catch(function (error) {
      console.error('Error updating progress:', error);
    });
}

// --- Sidebar ---
(function () {
  var sidebar = document.getElementById('mainSidebar');
  var sidebarToggle = document.getElementById('sidebarToggle');
  var mobileToggle = document.getElementById('mobileToggle');
  var sidebarOverlay = document.getElementById('sidebarOverlay');
  var searchInput = document.getElementById('sbSearchInput');
  var tooltip = document.getElementById('sbTooltip');

  if (!sidebar) return;

  // ── Restore collapsed state ──
  if (localStorage.getItem('sidebar-collapsed') === 'true') {
    sidebar.classList.add('collapsed');
    document.body.classList.add('sidebar-collapsed');
  }

  // ── Desktop collapse/expand toggle ──
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('collapsed');
      document.body.classList.toggle('sidebar-collapsed');
      localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
    });
  }

  // ── Mobile hamburger toggle ──
  if (mobileToggle) {
    mobileToggle.addEventListener('click', function () {
      sidebar.classList.toggle('mobile-open');
      if (sidebarOverlay) sidebarOverlay.classList.toggle('active');
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', function () {
      sidebar.classList.remove('mobile-open');
      sidebarOverlay.classList.remove('active');
    });
  }

  // ── Active link ──
  var currentPath = window.location.pathname;
  sidebar.querySelectorAll('.sidebar-link[href]').forEach(function (link) {
    var href = link.getAttribute('href');
    if (href && href === currentPath) {
      link.classList.add('active');
      // Ensure parent group is open
      var group = link.closest('.sb-group');
      if (group) {
        var items = group.querySelector('.sb-group-items');
        if (items) items.classList.add('open');
        var toggle = group.querySelector('.sb-group-toggle');
        if (toggle) toggle.setAttribute('aria-expanded', 'true');
      }
    }
  });

  // ── Collapsible groups ──
  sidebar.querySelectorAll('.sb-group-toggle').forEach(function (btn) {
    var group = btn.closest('.sb-group');
    var items = group ? group.querySelector('.sb-group-items') : null;
    var key = 'sb-group-' + (group ? group.getAttribute('data-group') : '');

    // Restore state — default open
    if (items) {
      var stored = localStorage.getItem(key);
      if (stored === 'closed') {
        items.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
      } else {
        items.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
      }
      // If group has active link, always open
      if (items.querySelector('.sidebar-link.active')) {
        items.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
      }
    }

    btn.addEventListener('click', function () {
      if (!items) return;
      var isOpen = items.classList.toggle('open');
      btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      localStorage.setItem(key, isOpen ? 'open' : 'closed');
    });
  });

  // ── Search / Filter ──
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      var q = this.value.toLowerCase().trim();
      sidebar.querySelectorAll('.sb-group').forEach(function (group) {
        var links = group.querySelectorAll('.sidebar-link');
        var anyVisible = false;
        links.forEach(function (link) {
          var text = (link.textContent || '').toLowerCase();
          var desc = (link.getAttribute('data-desc') || '').toLowerCase();
          var match = !q || text.indexOf(q) !== -1 || desc.indexOf(q) !== -1;
          link.classList.toggle('sb-hidden', !match);
          if (match) anyVisible = true;
        });
        group.classList.toggle('sb-hidden', !anyVisible);
        // Auto-open matching groups during search
        if (q && anyVisible) {
          var items = group.querySelector('.sb-group-items');
          if (items) items.classList.add('open');
        }
      });
      // Also filter top-level links (Home)
      sidebar.querySelectorAll('.sidebar-nav > .sidebar-link').forEach(function (link) {
        var text = (link.textContent || '').toLowerCase();
        var desc = (link.getAttribute('data-desc') || '').toLowerCase();
        var match = !q || text.indexOf(q) !== -1 || desc.indexOf(q) !== -1;
        link.classList.toggle('sb-hidden', !match);
      });
    });

    // Ctrl+K / Cmd+K shortcut
    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
      // Escape clears search
      if (e.key === 'Escape' && document.activeElement === searchInput) {
        searchInput.value = '';
        searchInput.dispatchEvent(new Event('input'));
        searchInput.blur();
      }
    });
  }

  // ── Collapsed-mode tooltips ──
  if (tooltip) {
    var hideTimer;
    sidebar.querySelectorAll('.sidebar-link').forEach(function (link) {
      link.addEventListener('mouseenter', function () {
        if (!sidebar.classList.contains('collapsed')) return;
        clearTimeout(hideTimer);
        var text = link.querySelector('.sidebar-text');
        var desc = link.getAttribute('data-desc');
        var name = text ? text.textContent.trim() : '';
        if (!name) return;

        tooltip.innerHTML = name + (desc ? '<span class="sb-tip-desc">' + desc + '</span>' : '');
        var rect = link.getBoundingClientRect();
        tooltip.style.left = (rect.right + 8) + 'px';
        tooltip.style.top = (rect.top + rect.height / 2) + 'px';
        tooltip.style.transform = 'translateY(-50%)';
        tooltip.classList.add('visible');
      });

      link.addEventListener('mouseleave', function () {
        hideTimer = setTimeout(function () {
          tooltip.classList.remove('visible');
        }, 80);
      });
    });
  }
}());