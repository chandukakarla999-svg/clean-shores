/**
 * CleanShores - Authentication & Profile Manager
 * Handles login, registration, password validation, and profile forms.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Password visibility toggle helpers
    const toggleBtns = document.querySelectorAll('.toggle-password-btn');
    toggleBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const input = document.getElementById(btn.getAttribute('data-target'));
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    btn.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';
                } else {
                    input.type = 'password';
                    btn.innerHTML = '<i class="fa-solid fa-eye"></i>';
                }
            }
        });
    });

    // Form submission loading state
    const authForms = document.querySelectorAll('.auth-form');
    authForms.forEach(function (form) {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.textContent.trim();
                submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';
            }
        });
    });
});
