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
  document.querySelectorAll('.timeline-card-header').forEach((header, idx) => {
    const entry  = header.closest('.timeline-entry');
    const body   = entry ? entry.querySelector('.timeline-card-body') : null;
    const expBtn = header.querySelector('.expand-btn');

    // Issue #5 (HIGH): the .expand-btn is a native <button> and would receive
    // its own Tab stop inside the header that already acts as a button.
    // Remove it from tab order and hide it from assistive technology;
    // the parent header handles all activation.
    if (expBtn) {
      expBtn.setAttribute('tabindex', '-1');
      expBtn.setAttribute('aria-hidden', 'true');
    }

    // Issue #11 (MEDIUM): link header to its controlled body via aria-controls
    if (body) {
      const bodyId = `timeline-body-${idx}`;
      body.id = bodyId;
      header.setAttribute('aria-controls', bodyId);
    }

    header.addEventListener('click', () => {
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

  /* ── Image fallback — proactive + reactive (Issue #2) ───── */
  // Apply data-fallback colour to the parent container IMMEDIATELY,
  // so there is never a blank white box while lazy images are loading.
  // The CSS also sets fallback backgrounds, but this JS pass handles
  // dynamic per-image colours declared in data-fallback.
  document.querySelectorAll('img[data-fallback]').forEach(img => {
    const color  = img.dataset.fallback || '#40916C';
    const parent = img.parentElement;
    if (parent && !img.complete) {
      parent.style.background = color;
    }

    // Also handle actual network failures: replace with a coloured div
    img.addEventListener('error', function () {
      const div = document.createElement('div');
      div.className = 'thumb-fallback';
      div.style.background = color;
      div.style.width  = '100%';
      div.style.height = '100%';
      if (this.parentNode) this.parentNode.replaceChild(div, this);
    });

    // Once the image loads successfully, clear the background so the image
    // shows through cleanly (no colour bleed around transparent edges)
    img.addEventListener('load', function () {
      if (this.parentElement) this.parentElement.style.background = '';
    });
  });

  // Generic error fallback for any image without data-fallback
  document.querySelectorAll('img:not([data-fallback])').forEach(img => {
    img.addEventListener('error', function () {
      this.classList.add('img-error');
      const parent = this.parentElement;
      if (parent) {
        parent.style.background = 'linear-gradient(135deg, #40916C 0%, #1B4332 100%)';
      }
    });
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
