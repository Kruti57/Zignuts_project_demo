/**
 * Central Action Tracker UI Engine
 * Real-time filtering, inline status cycling, live stats, and quick modals.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Inline Status Dropdown Change Listeners
  document.querySelectorAll('.inline-status-select').forEach(selectEl => {
    selectEl.addEventListener('change', (e) => {
      const actionId = selectEl.getAttribute('data-action-id');
      const newStatus = selectEl.value;
      updateActionStatus(actionId, newStatus, selectEl);
    });
  });

  function updateActionStatus(actionId, status, selectEl) {
    const originalValue = selectEl.getAttribute('data-original-val') || selectEl.value;
    selectEl.disabled = true;

    fetch(`/actions/${actionId}/update-status/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: new URLSearchParams({ 'status': status })
    })
    .then(res => {
      if (!res.ok) throw new Error('Status update failed');
      return res.json();
    })
    .then(data => {
      selectEl.disabled = false;
      selectEl.setAttribute('data-original-val', status);

      // Update badge or row visual state
      const row = document.getElementById(`action-row-${actionId}`);
      if (row) {
        if (status === 'COMPLETED') {
          row.classList.add('opacity-75');
          const taskDesc = row.querySelector('.task-description');
          if (taskDesc) taskDesc.classList.add('text-decoration-line-through', 'text-muted');
        } else {
          row.classList.remove('opacity-75');
          const taskDesc = row.querySelector('.task-description');
          if (taskDesc) taskDesc.classList.remove('text-decoration-line-through', 'text-muted');
        }
      }

      showToast(`Action status updated to ${data.status_display}`, 'success');
      refreshTrackerStats();
    })
    .catch(err => {
      selectEl.disabled = false;
      selectEl.value = originalValue;
      showToast('Error updating status: ' + err.message, 'danger');
    });
  }

  // 2. Dynamic Stats Refresh via API
  function refreshTrackerStats() {
    fetch('/api/dashboard/stats/')
      .then(res => res.json())
      .then(stats => {
        const totalEl = document.getElementById('stat-total-actions');
        const openEl = document.getElementById('stat-open-actions');
        const inProgEl = document.getElementById('stat-inprogress-actions');
        const compEl = document.getElementById('stat-completed-actions');
        const overdueEl = document.getElementById('stat-overdue-actions');

        if (totalEl) totalEl.textContent = stats.total_actions;
        if (openEl) openEl.textContent = stats.open_actions;
        if (inProgEl) inProgEl.textContent = stats.in_progress_actions;
        if (compEl) compEl.textContent = stats.completed_actions;
        if (overdueEl) overdueEl.textContent = stats.overdue_actions;
      })
      .catch(() => {});
  }

  // 3. Client-side Realtime Search Filter (complements server search)
  const searchInput = document.getElementById('tracker-search-input');
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const filterText = searchInput.value.toLowerCase().trim();
        const rows = document.querySelectorAll('.tracker-row');
        let visibleCount = 0;

        rows.forEach(row => {
          const content = row.textContent.toLowerCase();
          if (!filterText || content.includes(filterText)) {
            row.style.display = '';
            visibleCount++;
          } else {
            row.style.display = 'none';
          }
        });

        const noResultsRow = document.getElementById('no-search-results-row');
        if (noResultsRow) {
          noResultsRow.style.display = (visibleCount === 0 && rows.length > 0) ? '' : 'none';
        }
      }, 150);
    });
  }
});
