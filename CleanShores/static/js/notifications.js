/**
 * CleanShores - Notifications Manager
 * Handles async fetching, reading, and rendering of system notifications.
 */

async function loadNotifications() {
    const list = document.getElementById('notifList');
    if (!list) return;

    try {
        list.innerHTML = '<div class="notif-loading" style="padding:1rem;text-align:center;color:#64748b;"><i class="fa-solid fa-spinner fa-spin"></i> Loading...</div>';
        const res = await fetch('/api/notifications/recent');
        if (!res.ok) {
            list.innerHTML = '<div style="padding:1rem;text-align:center;color:#94a3b8;font-size:0.875rem;">Unable to load notifications.</div>';
            return;
        }

        const data = await res.json();
        const notifs = data.notifications || [];

        if (notifs.length === 0) {
            list.innerHTML = '<div class="notif-empty" style="padding:1.5rem 1rem;text-align:center;color:#64748b;font-size:0.875rem;"><i class="fa-regular fa-bell" style="font-size:1.5rem;display:block;margin-bottom:0.5rem;opacity:0.6;"></i>All caught up! No notifications.</div>';
            return;
        }

        list.innerHTML = notifs.map(function (n) {
            const iconMap = {
                registration: 'fa-user-plus',
                drive_update: 'fa-calendar',
                certificate: 'fa-award',
                message: 'fa-envelope',
                verification: 'fa-shield-halved',
                system: 'fa-bell'
            };
            const icon = iconMap[n.type] || 'fa-bell';
            const unreadClass = n.is_read ? '' : 'notif-unread';

            return `
                <div class="notif-item ${unreadClass}" onclick="markNotificationRead(${n.id}, '${n.link || ''}')" style="cursor:pointer;">
                    <div class="notif-item-icon">
                        <i class="fa-solid ${icon}"></i>
                    </div>
                    <div class="notif-item-body">
                        <strong>${escapeHtml(n.title)}</strong>
                        <p>${escapeHtml(n.message)}</p>
                        <span class="notif-time">${escapeHtml(n.created_at)}</span>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        console.error('Error fetching notifications:', err);
        list.innerHTML = '<div style="padding:1rem;text-align:center;color:#94a3b8;font-size:0.875rem;">Error loading notifications.</div>';
    }
}

async function markNotificationRead(id, link) {
    try {
        await fetch(`/api/notifications/${id}/read`, { method: 'POST' });
        if (link && link !== '#' && link !== '') {
            window.location.href = link;
        } else {
            // Update UI count badge if present
            const badge = document.querySelector('.notif-badge');
            if (badge) {
                const count = parseInt(badge.textContent, 10) - 1;
                if (count > 0) {
                    badge.textContent = count;
                } else {
                    badge.remove();
                }
            }
        }
    } catch (err) {
        console.error('Error marking notification read:', err);
        if (link && link !== '#') {
            window.location.href = link;
        }
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function (m) { return map[m]; });
}
