/**
 * SyncMind AI - Interactive 3D Tilt, Motion, Ripple & Card Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // =========================================================================
  // 1. Interactive 3D Tilt Engine
  // =========================================================================
  const tiltCards = document.querySelectorAll('[data-tilt], .tilt-card');

  tiltCards.forEach(card => {
    const maxTilt = parseFloat(card.getAttribute('data-tilt-max') || '8');
    let isHovering = false;

    card.addEventListener('mouseenter', () => {
      isHovering = true;
      card.style.transition = 'transform 0.1s ease-out, box-shadow 0.25s ease';
    });

    card.addEventListener('mousemove', (e) => {
      if (!isHovering) return;
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const percentX = (x - centerX) / centerX;
      const percentY = (y - centerY) / centerY;

      const rotateY = percentX * maxTilt;
      const rotateX = -percentY * maxTilt;

      card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale(1.01)`;
    });

    card.addEventListener('mouseleave', () => {
      isHovering = false;
      card.style.transition = 'transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease';
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)';
    });
  });

  // =========================================================================
  // 2. Interactive Flip Card Engine
  // =========================================================================
  document.querySelectorAll('.flip-trigger').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      // Don't flip if clicking an internal link or button
      if (e.target.closest('a') || e.target.closest('button') || e.target.closest('select')) {
        return;
      }
      const container = trigger.closest('.flip-card-container');
      if (container) {
        const inner = container.querySelector('.flip-card-inner');
        if (inner) {
          inner.classList.toggle('is-flipped');
        }
      }
    });
  });

  // Flip Back Buttons inside cards
  document.querySelectorAll('.flip-back-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const container = btn.closest('.flip-card-container');
      if (container) {
        const inner = container.querySelector('.flip-card-inner');
        if (inner) {
          inner.classList.remove('is-flipped');
        }
      }
    });
  });

  // =========================================================================
  // 3. Dynamic Ripple Wave on Click
  // =========================================================================
  const rippleButtons = document.querySelectorAll('.btn-primary-gradient, .btn-secondary-custom, .btn-ripple');

  rippleButtons.forEach(button => {
    button.addEventListener('click', function (e) {
      const rect = this.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const ripple = document.createElement('span');
      ripple.className = 'ripple-wave';
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;

      const diameter = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = `${diameter}px`;
      ripple.style.marginLeft = `-${diameter / 2}px`;
      ripple.style.marginTop = `-${diameter / 2}px`;

      this.appendChild(ripple);

      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
  });

  // =========================================================================
  // 4. Password Visibility Toggle
  // =========================================================================
  document.querySelectorAll('.toggle-password-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.getAttribute('data-target-input');
      const input = document.getElementById(targetId);
      const icon = btn.querySelector('i');

      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          if (icon) icon.className = 'bi bi-eye-slash text-primary';
        } else {
          input.type = 'password';
          if (icon) icon.className = 'bi bi-eye text-muted';
        }
      }
    });
  });

  // =========================================================================
  // 5. Scroll Animations with IntersectionObserver
  // =========================================================================
  const scrollElements = document.querySelectorAll('.animate-on-scroll');

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries, observerInstance) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const animClass = entry.target.getAttribute('data-animation') || 'anim-fade-up';
          entry.target.classList.add(animClass);
          observerInstance.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });

    scrollElements.forEach(el => observer.observe(el));
  } else {
    scrollElements.forEach(el => el.classList.add('anim-fade-up'));
  }

  // =========================================================================
  // 6. Universal Animated Number Counters (Count 0 -> Target)
  // =========================================================================
  function animateValue(element, start, end, duration, decimals = 0, suffix = '') {
    if (isNaN(end)) return;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Easing function: easeOutCubic (1 - (1 - t)^3)
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * easeOut;

      if (decimals > 0) {
        element.textContent = current.toFixed(decimals) + suffix;
      } else {
        element.textContent = Math.round(current).toLocaleString() + suffix;
      }

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        if (decimals > 0) {
          element.textContent = end.toFixed(decimals) + suffix;
        } else {
          element.textContent = Math.round(end).toLocaleString() + suffix;
        }
      }
    }

    requestAnimationFrame(update);
  }

  window.runNumberCounters = function() {
    const counterElements = document.querySelectorAll(
      '[data-counter-target], .counter-number, .stat-val, .stat-card h3, [id^="stat-"]'
    );

    counterElements.forEach(el => {
      let rawTarget = el.getAttribute('data-counter-target');
      let suffix = el.getAttribute('data-counter-suffix') || '';

      if (!rawTarget) {
        const text = el.textContent.trim();
        if (text.endsWith('%')) {
          suffix = '%';
          rawTarget = text.replace('%', '').trim();
        } else {
          rawTarget = text.replace(/[^0-9.]/g, '');
        }
      }

      const target = parseFloat(rawTarget);
      if (isNaN(target)) return;

      const isDecimal = rawTarget.toString().includes('.') || target % 1 !== 0;
      const decimals = isDecimal ? 1 : 0;

      // Smoothly animate from 0 to target number
      animateValue(el, 0, target, 1300, decimals, suffix);
    });
  };

  // Run on page load
  window.runNumberCounters();
});
