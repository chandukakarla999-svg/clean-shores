/**
 * CleanShores - Drives Directory & Filtering JavaScript
 * Enhances the Browse Drives page with dynamic search, responsive card interactions, and category filtering.
 */

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('.filter-input-search');
    const filterForm = document.getElementById('filterForm');
    const drivesGrid = document.getElementById('drivesGrid');

    // Auto-focus search input with smooth interaction
    if (searchInput) {
        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                filterForm.submit();
            }
        });
    }

    // Animate drive cards on appearance
    const cards = document.querySelectorAll('.drive-card');
    if (cards.length > 0) {
        cards.forEach(function (card, index) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(12px)';
            card.style.transition = 'opacity 0.35s ease, transform 0.35s ease, box-shadow 0.25s ease';
            setTimeout(function () {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 40 * index);
        });
    }

    // Confirmation on drive registration
    const registerForms = document.querySelectorAll('form[action*="register_for_drive"]');
    registerForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Joining...';
            }
        });
    });
});
