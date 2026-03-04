/* ============================================================
   Laos Events — main.js
   Timeline accordion, sticky nav, scroll animations, image fallbacks
   ============================================================ */

(function () {
  'use strict';

  // Remove no-js class if JS is running
  document.documentElement.classList.remove('no-js');

  /* ── Sticky nav ───────────────────────────────────────────── */
  const nav = document.querySelector('.site-nav');
  if (nav) {
    const onScroll = () => {
      nav.classList.toggle('scrolled', window.scrollY > 60);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ── Mobile nav toggle ────────────────────────────────────── */
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', () => {
      const open = navLinks.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    // Close on link click
    navLinks.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => navLinks.classList.remove('open'));
    });
  }

  /* ── Timeline accordion ──────────────────────────────────── */
  document.querySelectorAll('.timeline-card-header').forEach(header => {
    header.addEventListener('click', () => {
      const entry = header.closest('.timeline-entry');
      if (!entry) return;
      const isOpen = entry.classList.contains('open');
      // Collapse all others
      document.querySelectorAll('.timeline-entry.open').forEach(e => {
        if (e !== entry) e.classList.remove('open');
      });
      entry.classList.toggle('open', !isOpen);
    });
    // Keyboard support
    header.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        header.click();
      }
    });
    header.setAttribute('role', 'button');
    header.setAttribute('tabindex', '0');
    header.setAttribute('aria-expanded', 'false');
  });

  // Keep aria-expanded in sync
  document.querySelectorAll('.timeline-entry').forEach(entry => {
    const header = entry.querySelector('.timeline-card-header');
    if (!header) return;
    const observer = new MutationObserver(() => {
      header.setAttribute('aria-expanded', String(entry.classList.contains('open')));
    });
    observer.observe(entry, { attributes: true, attributeFilter: ['class'] });
  });

  /* ── Scroll-reveal (IntersectionObserver) ─────────────────── */
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!prefersReduced && 'IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.fade-in').forEach(el => revealObserver.observe(el));
  } else {
    // If reduced motion or no IO, show everything immediately
    document.querySelectorAll('.fade-in').forEach(el => el.classList.add('visible'));
  }

  /* ── Image error fallback ────────────────────────────────── */
  document.querySelectorAll('img[data-fallback]').forEach(img => {
    img.addEventListener('error', function () {
      const fallbackColor = this.dataset.fallback || '#40916C';
      // Replace broken img with a colored div
      const div = document.createElement('div');
      div.className = 'thumb-fallback';
      div.style.background = fallbackColor;
      this.parentNode.replaceChild(div, this);
    });
  });

  // Generic image error: hide broken images gracefully
  document.querySelectorAll('img').forEach(img => {
    if (!img.dataset.fallback) {
      img.addEventListener('error', function () {
        this.classList.add('img-error');
        // Try to apply a background to the parent
        const parent = this.parentElement;
        if (parent) {
          parent.style.background = 'linear-gradient(135deg, #40916C 0%, #1B4332 100%)';
        }
      });
    }
  });

  /* ── Smooth scroll for anchor links ──────────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const navHeight = nav ? nav.getBoundingClientRect().height : 0;
        const top = target.getBoundingClientRect().top + window.scrollY - navHeight - 16;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

})();
