// ── Menu hamburger ──────────────────────────────────────────────
document.querySelector('.menu-toggle').addEventListener('click', function () {
  document.querySelector('.nav-links').classList.toggle('open');
});

// ── Lightbox ─────────────────────────────────────────────────────
(function () {
  function openLightbox(src, alt) {
    const overlay = document.createElement('div');
    overlay.className = 'lb-overlay';

    const img = document.createElement('img');
    img.src = src;
    img.alt = alt || '';
    img.className = 'lb-img';

    const close = document.createElement('button');
    close.className = 'lb-close';
    close.innerHTML = '&times;';
    close.setAttribute('aria-label', 'Fermer');

    overlay.appendChild(img);
    overlay.appendChild(close);
    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';

    requestAnimationFrame(() => overlay.classList.add('lb-active'));

    function closeLb() {
      overlay.classList.remove('lb-active');
      overlay.addEventListener('transitionend', () => {
        overlay.remove();
        document.body.style.overflow = '';
      }, { once: true });
    }

    close.addEventListener('click', closeLb);
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeLb();
    });
    document.addEventListener('keydown', function onKey(e) {
      if (e.key === 'Escape') { closeLb(); document.removeEventListener('keydown', onKey); }
    });
  }

  // Active le lightbox sur toutes les images des galeries d'articles
  document.querySelectorAll('.article-gallery img').forEach(function (img) {
    img.style.cursor = 'zoom-in';
    img.addEventListener('click', function () {
      openLightbox(img.src, img.alt);
    });
  });
})();
