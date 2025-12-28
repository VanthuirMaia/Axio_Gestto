// Global function for sidebar toggle (called from inline onclick)
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");

  if (window.innerWidth < 992) {
    // Mobile: show/hide
    sidebar.classList.toggle("show");
    overlay.classList.toggle("show");
    // Prevent body scroll when menu is open
    document.body.style.overflow = sidebar.classList.contains("show") ? "hidden" : "";
  } else {
    // Desktop: collapse/expand
    sidebar.classList.toggle("collapsed");
    // Save state to localStorage
    const isCollapsed = sidebar.classList.contains("collapsed");
    localStorage.setItem("sidebarCollapsed", isCollapsed);
  }
}

// Sidebar functionality
document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");

  // Load saved collapsed state
  const savedState = localStorage.getItem("sidebarCollapsed");
  if (savedState === "true" && window.innerWidth >= 992) {
    sidebar.classList.add("collapsed");
  }

  // Mobile menu button (from base.html topbar)
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener("click", toggleSidebar);
  }

  // Overlay click
  if (overlay) {
    overlay.addEventListener("click", toggleSidebar);
  }

  // Close mobile sidebar when clicking on a link
  if (sidebar) {
    const navLinks = sidebar.querySelectorAll(".nav-link");
    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        if (window.innerWidth < 992 && sidebar.classList.contains("show")) {
          sidebar.classList.remove("show");
          overlay.classList.remove("show");
          document.body.style.overflow = "";
        }
      });
    });
  }

  // Close on Escape key (mobile)
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && sidebar && sidebar.classList.contains("show")) {
      sidebar.classList.remove("show");
      overlay.classList.remove("show");
      document.body.style.overflow = "";
    }
  });
});
