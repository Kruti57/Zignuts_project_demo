/**
 * Main application utilities: CSRF, Toasts, Delete Confirmations, Tooltips.
 */

// CSRF Cookie extraction
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Toast Notification Manager
function showToast(message, type = 'success', title = '') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toastId = 'toast-' + Date.now();
  const bgClass = type === 'success' ? 'text-bg-success' :
                  type === 'danger' || type === 'error' ? 'text-bg-danger' :
                  type === 'warning' ? 'text-bg-warning' : 'text-bg-primary';

  const iconClass = type === 'success' ? 'bi-check-circle-fill' :
                    type === 'danger' || type === 'error' ? 'bi-exclamation-triangle-fill' :
                    type === 'warning' ? 'bi-exclamation-circle-fill' : 'bi-info-circle-fill';

  const headerTitle = title || (type === 'success' ? 'Success' : type === 'error' || type === 'danger' ? 'Error' : 'Notification');

  const toastEl = document.createElement('div');
  toastEl.className = `toast align-items-center ${bgClass} border-0 mb-2 shadow-lg`;
  toastEl.id = toastId;
  toastEl.setAttribute('role', 'alert');
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.setAttribute('aria-atomic', 'true');

  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body d-flex align-items-center gap-2">
        <i class="bi ${iconClass} fs-5"></i>
        <div>
          <div class="fw-bold">${headerTitle}</div>
          <div class="small">${message}</div>
        </div>
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;

  container.appendChild(toastEl);
  const bsToast = new bootstrap.Toast(toastEl, { delay: 4000 });
  bsToast.show();

  toastEl.addEventListener('hidden.bs.toast', () => {
    toastEl.remove();
  });
}

// Copy to Clipboard Utility
function copyToClipboard(text, buttonElement) {
  if (!navigator.clipboard) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      showToast('Copied to clipboard!', 'success');
    } catch (err) {
      showToast('Failed to copy', 'error');
    }
    document.body.removeChild(textArea);
    return;
  }

  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied to clipboard!', 'success');
    if (buttonElement) {
      const origHtml = buttonElement.innerHTML;
      buttonElement.innerHTML = '<i class="bi bi-check2"></i> Copied!';
      setTimeout(() => {
        buttonElement.innerHTML = origHtml;
      }, 2000);
    }
  }).catch(() => {
    showToast('Failed to copy to clipboard', 'error');
  });
}

// Initialize Bootstrap Tooltips & Confirm Modals
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Global Delete Confirmation Modal Handler
  const deleteModalEl = document.getElementById('globalDeleteModal');
  if (deleteModalEl) {
    const deleteForm = document.getElementById('globalDeleteForm');
    const deleteItemName = document.getElementById('globalDeleteItemName');
    
    document.querySelectorAll('[data-bs-target="#globalDeleteModal"]').forEach(button => {
      button.addEventListener('click', () => {
        const actionUrl = button.getAttribute('data-delete-url');
        const itemName = button.getAttribute('data-item-name') || 'this item';
        
        if (deleteForm) deleteForm.setAttribute('action', actionUrl);
        if (deleteItemName) deleteItemName.textContent = itemName;
      });
    });
  }

  // Global Employee / Assignee Dropdown Picker Handler
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.select-owner-btn');
    if (btn) {
      e.preventDefault();
      const ownerName = btn.getAttribute('data-owner-name');
      const targetInputId = btn.getAttribute('data-target-input');
      let input = targetInputId ? document.getElementById(targetInputId) : null;
      if (!input) {
        input = btn.closest('.input-group') ? btn.closest('.input-group').querySelector('input') : null;
      }
      if (input && ownerName) {
        input.value = ownerName;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
  });
});
