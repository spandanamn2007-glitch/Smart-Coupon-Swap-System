/**
 * Smart Coupon Swap System — Dashboard JavaScript
 * Handles all API calls and dynamic rendering for the dashboard pages.
 * Uses fetch() with credentials: 'include' for session cookie auth.
 */

/* ============================================================
   UTILITIES
   ============================================================ */

function apiError(msg) {
    return `<div class="alert alert-warning py-2 mb-0"><i class="bi bi-exclamation-circle me-1"></i>${msg}</div>`;
}

function emptyState(msg, icon='inbox') {
    return `<div class="text-center text-muted py-4"><i class="bi bi-${icon} fs-2 d-block mb-2"></i>${msg}</div>`;
}

function redirectToLogin() {
    window.location.href = '/';
}

async function apiFetch(url, options={}) {
    const res = await fetch(url, {credentials: 'include', ...options});
    if (res.status === 401) { redirectToLogin(); return null; }
    return res;
}

/* ============================================================
   USER DASHBOARD
   ============================================================ */

async function loadUserDashboard() {
    await Promise.all([
        loadProfile(),
        loadMyCoupons(),
        loadNotifications(),
        loadRecommendations()
    ]);
}

async function loadProfile() {
    const el = document.getElementById('profile-section');
    const repEl = document.getElementById('stat-reputation');
    try {
        const res = await apiFetch('/api/users/profile');
        if (!res || !res.ok) { el.innerHTML = apiError('Could not load profile'); return; }
        const data = await res.json();
        const u = data.user;
        document.getElementById('welcome-msg').textContent = `Welcome back, ${u.name}`;
        repEl.textContent = parseFloat(u.reputation_score || 0).toFixed(2);
        el.innerHTML = `
            <p><span class="label">Name</span>${escHtml(u.name)}</p>
            <p><span class="label">Email</span>${escHtml(u.email)}</p>
            <p><span class="label">Role</span><span class="badge bg-secondary">${escHtml(u.role_name || '')}</span></p>
            <p><span class="label">City</span>${escHtml(u.city || '—')}</p>
            <p><span class="label">State</span>${escHtml(u.state || '—')}</p>
            <p><span class="label">Status</span><span class="badge bg-${u.status === 'ACTIVE' ? 'success' : 'danger'}">${escHtml(u.status)}</span></p>
            <p><span class="label">Member Since</span>${escHtml(String(u.created_at || '').substring(0, 10))}</p>
        `;
    } catch(e) {
        el.innerHTML = apiError('Failed to load profile.');
    }
}

async function loadMyCoupons() {
    const tbody = document.getElementById('coupons-table-body');
    const statEl = document.getElementById('stat-coupons');
    try {
        const res = await apiFetch('/api/coupons?status=ACTIVE');
        if (!res || !res.ok) { tbody.innerHTML = `<tr><td colspan="6">${apiError('Could not load coupons')}</td></tr>`; return; }
        const data = await res.json();
        const sessionRes = await apiFetch('/api/auth/me');
        let myUserId = null;
        if (sessionRes && sessionRes.ok) {
            const me = await sessionRes.json();
            myUserId = me.user_id;
        }
        // Filter to own coupons (owner_id matching session user)
        const coupons = myUserId
            ? data.coupons.filter(c => c.owner_id === myUserId)
            : data.coupons;
        statEl.textContent = coupons.length;
        if (coupons.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6">${emptyState('No active coupons found.')}</td></tr>`;
            return;
        }
        tbody.innerHTML = coupons.map(c => `
            <tr>
                <td>${escHtml(c.title)}</td>
                <td><span class="badge bg-secondary">${escHtml(c.category_name || '')}</span></td>
                <td>${escHtml(c.brand_name || '')}</td>
                <td><strong>${escHtml(String(c.discount_type))}</strong> ${parseFloat(c.discount_value).toFixed(2)}</td>
                <td>${escHtml(String(c.expiry_date || '').substring(0, 10))}</td>
                <td><span class="badge bg-${c.status === 'ACTIVE' ? 'success' : 'secondary'}">${escHtml(c.status)}</span></td>
            </tr>
        `).join('');
    } catch(e) {
        tbody.innerHTML = `<tr><td colspan="6">${apiError('Failed to load coupons.')}</td></tr>`;
    }
}

async function loadNotifications() {
    const list = document.getElementById('notifications-list');
    const statEl = document.getElementById('stat-notifications');
    try {
        const res = await apiFetch('/api/notifications?limit=8');
        if (!res || !res.ok) { list.innerHTML = `<li class="list-group-item">${apiError('Could not load notifications')}</li>`; return; }
        const data = await res.json();
        statEl.textContent = data.count || 0;
        if (!data.notifications || data.notifications.length === 0) {
            list.innerHTML = `<li class="list-group-item">${emptyState('No notifications yet.', 'bell-slash')}</li>`;
            return;
        }
        list.innerHTML = data.notifications.map(n => `
            <li class="list-group-item ${n.is_read ? '' : 'fw-semibold'}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <span class="badge bg-${notifTypeBadge(n.type)} me-1">${escHtml(n.type || 'SYSTEM')}</span>
                        ${escHtml(n.title)}
                    </div>
                    ${n.is_read ? '' : '<span class="badge bg-primary rounded-pill">New</span>'}
                </div>
                <small class="text-muted">${escHtml(String(n.created_at || '').substring(0, 10))}</small>
            </li>
        `).join('');
    } catch(e) {
        list.innerHTML = `<li class="list-group-item">${apiError('Failed to load notifications.')}</li>`;
    }
}

async function loadRecommendations() {
    const list = document.getElementById('recs-list');
    const statEl = document.getElementById('stat-recs');
    try {
        const res = await apiFetch('/api/recommendations');
        if (!res || !res.ok) { list.innerHTML = `<li class="list-group-item">${apiError('Could not load recommendations')}</li>`; return; }
        const data = await res.json();
        const recs = data.recommendations || [];
        statEl.textContent = recs.length;
        if (recs.length === 0) {
            list.innerHTML = `<li class="list-group-item">${emptyState('No recommendations yet. Add category preferences.', 'lightbulb-off')}</li>`;
            return;
        }
        list.innerHTML = recs.slice(0, 6).map(r => `
            <li class="list-group-item">
                <div class="d-flex justify-content-between">
                    <strong>${escHtml(r.coupon?.title || 'Coupon')}</strong>
                    <span class="badge bg-info">${r.recommendation_score} pts</span>
                </div>
                <small class="text-muted">${escHtml(r.explanation || '')}</small>
            </li>
        `).join('');
    } catch(e) {
        list.innerHTML = `<li class="list-group-item">${apiError('Failed to load recommendations.')}</li>`;
    }
}

function notifTypeBadge(type) {
    const map = {
        SWAP_PROPOSAL: 'primary', SWAP_ACCEPTED: 'success', SWAP_REJECTED: 'danger',
        SWAP_COMPLETED: 'success', COUPON_EXPIRING: 'warning', SMART_MATCH_FOUND: 'info',
        SYSTEM_ALERT: 'secondary'
    };
    return map[type] || 'secondary';
}

/* ============================================================
   ANALYTICS DASHBOARD
   ============================================================ */

let predChart = null;
let demandChart = null;

async function loadAnalyticsDashboard() {
    await Promise.all([loadAnomalies(), loadCycles()]);
}

async function loadAnomalies() {
    const tbody = document.getElementById('anomaly-table-body');
    const badge = document.getElementById('anomaly-badge');
    try {
        const res = await apiFetch('/api/predictions/anomalies?limit=15');
        if (!res || !res.ok) {
            tbody.innerHTML = `<tr><td colspan="7">${apiError('Could not load anomaly data')}</td></tr>`;
            return;
        }
        const data = await res.json();
        const users = data.anomalous_users || [];
        badge.textContent = `${data.total_anomalies_detected || 0} / ${data.total_users_scanned || 0} users`;
        if (users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7">${emptyState('No anomalous users detected.')}</td></tr>`;
            return;
        }
        tbody.innerHTML = users.map(u => `
            <tr>
                <td>#${u.user_id}</td>
                <td>${u.age}</td>
                <td><span class="badge bg-secondary">${escHtml(u.activity_level || '—')}</span></td>
                <td>${u.total_views}</td>
                <td>${u.swaps_proposed}</td>
                <td class="anomaly-score-low">${parseFloat(u.anomaly_score).toFixed(4)}</td>
                <td><span class="badge bg-warning text-dark">potential anomaly</span></td>
            </tr>
        `).join('');
    } catch(e) {
        tbody.innerHTML = `<tr><td colspan="7">${apiError('Failed to load anomaly data.')}</td></tr>`;
    }
}

async function loadCycles() {
    const container = document.getElementById('cycles-container');
    const badge = document.getElementById('cycle-count-badge');
    const cyclesBadge = document.getElementById('cycles-badge');
    try {
        const res = await apiFetch('/api/swaps/cycles');
        if (!res || !res.ok) {
            container.innerHTML = apiError('Could not load cycle data.');
            return;
        }
        const data = await res.json();
        const cycles = data.cycles || [];
        if (badge) badge.textContent = `${cycles.length} cycle(s) detected`;
        if (cyclesBadge) cyclesBadge.textContent = `${cycles.length} cycle(s)`;
        if (cycles.length === 0) {
            container.innerHTML = emptyState('No circular swap cycles detected in current active requests.', 'diagram-3');
            return;
        }
        container.innerHTML = cycles.map((c, i) => `
            <div class="alert alert-info mb-2">
                <strong><i class="bi bi-diagram-3 me-1"></i>${c.description}</strong>
                <div class="mt-1 small">
                    ${c.cycle_steps.map(s => `User <strong>#${s.from_user_id}</strong> → <em>${escHtml(s.coupon_title || '')}</em> → User <strong>#${s.to_user_id}</strong>`).join(' | ')}
                </div>
            </div>
        `).join('');
    } catch(e) {
        container.innerHTML = apiError('Failed to load swap cycle data.');
    }
}

async function runAcceptancePrediction() {
    const payload = {
        offered_value: parseFloat(document.getElementById('pred-offered').value),
        requested_value: parseFloat(document.getElementById('pred-requested').value),
        category_match: parseInt(document.getElementById('pred-cat').value),
        brand_match: parseInt(document.getElementById('pred-brand').value),
        proposer_rating: parseFloat(document.getElementById('pred-p-rating').value),
        receiver_rating: parseFloat(document.getElementById('pred-r-rating').value)
    };
    try {
        const res = await apiFetch('/api/predictions/acceptance', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        if (!res || !res.ok) { alert('Prediction failed. Please try again.'); return; }
        const data = await res.json();
        const prob = data.acceptance_probability || 0;
        document.getElementById('pred-result').style.display = '';
        const label = document.getElementById('pred-label');
        label.innerHTML = `Acceptance Probability: <span class="text-${prob >= 0.5 ? 'success' : 'danger'}">${(prob*100).toFixed(1)}%</span>
            ${data.is_likely_accepted ? '<span class="badge bg-success ms-2">Likely Accepted</span>' : '<span class="badge bg-danger ms-2">Likely Rejected</span>'}`;
        // Chart
        if (predChart) predChart.destroy();
        const ctx = document.getElementById('pred-chart').getContext('2d');
        predChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Acceptance', 'Rejection'],
                datasets: [{
                    data: [Math.round(prob*100), Math.round((1-prob)*100)],
                    backgroundColor: ['#198754', '#dc3545'],
                    borderWidth: 0
                }]
            },
            options: {plugins: {legend: {position: 'bottom'}}, cutout: '65%'}
        });
    } catch(e) {
        alert('Network error.');
    }
}

async function runDemandForecast() {
    const prev = parseFloat(document.getElementById('demand-prev').value);
    try {
        const res = await apiFetch('/api/predictions/demand', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({prev_month_requests: prev})
        });
        if (!res || !res.ok) { alert('Forecast failed.'); return; }
        const data = await res.json();
        const predicted = data.forecasted_next_month_requests || 0;
        document.getElementById('demand-result').style.display = '';
        if (demandChart) demandChart.destroy();
        const ctx = document.getElementById('demand-chart').getContext('2d');
        demandChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Previous Month', 'Forecasted Next Month'],
                datasets: [{
                    label: 'Requests',
                    data: [prev, predicted],
                    backgroundColor: ['#0d6efd', '#198754'],
                    borderRadius: 6
                }]
            },
            options: {
                plugins: {legend: {display: false}},
                scales: {y: {beginAtZero: true, title: {display: true, text: 'Request Count'}}}
            }
        });
    } catch(e) {
        alert('Network error.');
    }
}

/* ============================================================
   ADMIN DASHBOARD
   ============================================================ */

async function loadAdminDashboard() {
    await Promise.all([loadAdminStats(), loadAdminAnomalies()]);
}

async function loadAdminStats() {
    try {
        const res = await apiFetch('/api/admin/stats');
        if (!res) return;
        if (res.status === 403) {
            document.getElementById('admin-stats-row').innerHTML = apiError('Access denied. Admin role required.');
            return;
        }
        if (!res.ok) return;
        const data = await res.json();
        const s = data.stats;
        document.getElementById('stat-total-users').textContent = s.total_users || 0;
        document.getElementById('stat-active-users-badge').textContent = `${s.active_users || 0} Active`;
        document.getElementById('stat-total-coupons').textContent = s.total_coupons || 0;
        document.getElementById('stat-active-coupons-badge').textContent = `${s.active_coupons || 0} Active`;
        document.getElementById('stat-total-swaps').textContent = s.total_swaps || 0;
        document.getElementById('stat-completed-swaps-badge').textContent = `${s.completed_swaps || 0} Completed`;
        document.getElementById('stat-total-requests').textContent = s.total_requests || 0;
        document.getElementById('stat-open-reports-badge').textContent = `${s.open_reports || 0} Open Reports`;

        // Overview chart
        const ctx1 = document.getElementById('admin-overview-chart').getContext('2d');
        new Chart(ctx1, {
            type: 'doughnut',
            data: {
                labels: ['Users', 'Coupons', 'Requests', 'Swaps'],
                datasets: [{
                    data: [s.total_users, s.total_coupons, s.total_requests, s.total_swaps],
                    backgroundColor: ['#0d6efd', '#17a2b8', '#6c757d', '#198754'],
                    borderWidth: 0
                }]
            },
            options: {plugins: {legend: {position: 'bottom'}}, cutout: '60%'}
        });

        // Coupon status chart
        const ctx2 = document.getElementById('admin-coupons-chart').getContext('2d');
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: ['Total', 'Active'],
                datasets: [{
                    label: 'Coupons',
                    data: [s.total_coupons, s.active_coupons],
                    backgroundColor: ['#6c757d', '#198754'],
                    borderRadius: 6
                }]
            },
            options: {plugins: {legend: {display: false}}, scales: {y: {beginAtZero: true}}}
        });
    } catch(e) {
        document.getElementById('admin-stats-row').innerHTML = apiError('Failed to load system stats.');
    }
}

async function loadAdminAnomalies() {
    const container = document.getElementById('admin-anomalies-container');
    try {
        const res = await apiFetch('/api/predictions/anomalies?limit=5');
        if (!res || !res.ok) { container.innerHTML = apiError('Could not load anomaly data'); return; }
        const data = await res.json();
        container.innerHTML = `
            <div class="d-flex gap-3 mb-3">
                <div class="text-center px-3">
                    <h4 class="fw-bold text-warning mb-0">${data.total_anomalies_detected || 0}</h4>
                    <small class="text-muted">Potential Anomalies</small>
                </div>
                <div class="text-center px-3">
                    <h4 class="fw-bold text-primary mb-0">${data.total_users_scanned || 0}</h4>
                    <small class="text-muted">Users Scanned</small>
                </div>
                <div class="text-center px-3">
                    <h4 class="fw-bold text-secondary mb-0">5%</h4>
                    <small class="text-muted">Contamination Rate</small>
                </div>
            </div>
            <p class="text-muted small mb-0">Top flagged users shown. Use Analytics dashboard for full details.</p>
        `;
    } catch(e) {
        container.innerHTML = apiError('Failed to load anomaly summary.');
    }
}

/* ============================================================
   XSS PREVENTION
   ============================================================ */

function escHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
