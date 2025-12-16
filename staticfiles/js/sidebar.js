// Sidebar toggle functionality
document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const sidebarClose = document.getElementById("sidebarClose");
  const sidebarToggle = document.getElementById("sidebarToggle");

  // Toggle mobile sidebar
  function toggleMobileSidebar() {
    sidebar.classList.toggle("show");
    overlay.classList.toggle("show");
  }

  // Toggle desktop sidebar (collapsed/expanded)
  function toggleDesktopSidebar() {
    sidebar.classList.toggle("collapsed");
    // Save state to localStorage
    const isCollapsed = sidebar.classList.contains("collapsed");
    localStorage.setItem("sidebarCollapsed", isCollapsed);
  }

  // Load saved state
  const savedState = localStorage.getItem("sidebarCollapsed");
  if (savedState === "true") {
    sidebar.classList.add("collapsed");
  }

  // Event listeners
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener("click", toggleMobileSidebar);
  }

  if (sidebarClose) {
    sidebarClose.addEventListener("click", toggleMobileSidebar);
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", toggleDesktopSidebar);
  }

  if (overlay) {
    overlay.addEventListener("click", toggleMobileSidebar);
  }

  // Close mobile sidebar when clicking on a link
  if (window.innerWidth < 992) {
    const navLinks = sidebar.querySelectorAll(".nav-link");
    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        sidebar.classList.remove("show");
        overlay.classList.remove("show");
      });
    });
  }
});
