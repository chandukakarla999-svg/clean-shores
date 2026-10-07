/**
 * CleanShores - Dashboard Interactivity & Analytics
 * Powers dynamic metrics, chart rendering, and status card interactions.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Stat card counter animations
    const statValues = document.querySelectorAll('.stat-number, .stat-card-value');
    statValues.forEach(function (stat) {
        const text = stat.textContent.trim();
        const num = parseFloat(text.replace(/[^0-9.]/g, ''));
        if (!isNaN(num) && num > 0 && num < 100000) {
            let current = 0;
            const step = Math.max(1, Math.floor(num / 30));
            const timer = setInterval(function () {
                current += step;
                if (current >= num) {
                    current = num;
                    clearInterval(timer);
                }
                const suffix = text.includes('kg') ? ' kg' : (text.includes('%') ? '%' : '');
                stat.textContent = current.toLocaleString() + suffix;
            }, 25);
        }
    });

    // Sidebar active item highlight
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});
