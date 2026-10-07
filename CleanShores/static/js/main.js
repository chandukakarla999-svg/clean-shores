/**
 * CleanShores - Main Platform JavaScript
 * Handles global UI interactions, navigation, flash alerts, and accessible controls.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Mobile navigation drawer toggle
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('open');
            navToggle.classList.toggle('active');
        });
    }

    // Auto-dismiss flash alert messages
    const flashAlerts = document.querySelectorAll('.flash-alert');
    if (flashAlerts.length > 0) {
        setTimeout(function () {
            flashAlerts.forEach(function (alert) {
                alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(function () {
                    alert.remove();
                }, 400);
            });
        }, 5000);
    }

    // Navbar scroll background tint
    const mainNav = document.getElementById('mainNav');
    if (mainNav) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 40) {
                mainNav.classList.add('scrolled');
            } else {
                mainNav.classList.remove('scrolled');
            }
        }, { passive: true });
    }

    // Close open dropdowns when clicking outside
    document.addEventListener('click', function (e) {
        const userMenu = document.getElementById('userMenu');
        const userDropdown = document.getElementById('userDropdown');
        if (userMenu && userDropdown && !userMenu.contains(e.target)) {
            userDropdown.style.display = 'none';
        }

        const notifDropdown = document.getElementById('notifDropdown');
        const notifPanel = document.getElementById('notifPanel');
        if (notifDropdown && notifPanel && !notifDropdown.contains(e.target)) {
            notifPanel.style.display = 'none';
        }
    });
});
