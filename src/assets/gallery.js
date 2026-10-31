// Enhance the Lab photo strip; links and native scrolling work without JavaScript.
document.querySelectorAll('[data-gallery]').forEach(gallery => {
  const track = gallery.querySelector('.gallery-track');
  const scrollbar = gallery.querySelector('[data-gallery-scrollbar]');
  const dialog = gallery.querySelector('dialog');
  const fullImage = dialog.querySelector('[data-gallery-full]');
  const player = dialog.querySelector('[data-gallery-player]');
  const caption = dialog.querySelector('[data-gallery-caption]');
  let drag = null;
  let suppressClick = false;
  let animation = 0;
  let target = track.scrollLeft;
  let wheelDirection = 0;
  let wheelTimer;

  const updateControls = () => {
    scrollbar.max = Math.max(0, track.scrollWidth - track.clientWidth);
    scrollbar.value = track.scrollLeft;
    scrollbar.disabled = Number(scrollbar.max) <= 1;
  };
  const stopMotion = () => {
    cancelAnimationFrame(animation);
    animation = 0;
    target = track.scrollLeft;
  };
  const move = direction => {
    const item = track.querySelector('.gallery-item');
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    const maximum = track.scrollWidth - track.clientWidth;
    const start = track.scrollLeft;
    target = Math.max(0, Math.min(maximum,
      (animation ? target : start) + direction * (item.getBoundingClientRect().width + gap)));
    cancelAnimationFrame(animation);
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
      track.scrollLeft = target;
      animation = 0;
      return;
    }
    const destination = target;
    const started = performance.now();
    const tick = now => {
      const progress = Math.min(1, (now - started) / 500);
      const eased = progress * progress * (3 - 2 * progress);
      track.scrollLeft = start + (destination - start) * eased;
      animation = progress < 1 ? requestAnimationFrame(tick) : 0;
    };
    animation = requestAnimationFrame(tick);
  };
  scrollbar.addEventListener('input', () => {
    stopMotion();
    track.scrollLeft = Number(scrollbar.value);
  });
  track.addEventListener('scroll', updateControls, { passive: true });
  new ResizeObserver(() => { stopMotion(); updateControls(); }).observe(track);
  track.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      move(event.key === 'ArrowRight' ? 1 : -1);
    }
  });

  // Treat a vertical wheel burst as one photo step; preserve horizontal trackpad deltas.
  gallery.addEventListener('wheel', event => {
    if (dialog.open || event.ctrlKey || !matchMedia('(min-width: 768px)').matches) return;
    // Contain every desktop wheel event, including at the first and last photo.
    event.preventDefault();
    if (Math.abs(event.deltaX) > Math.abs(event.deltaY)) {
      stopMotion();
      const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? track.clientWidth : 1;
      track.scrollLeft += event.deltaX * unit;
      return;
    }
    const direction = Math.sign(event.deltaY);
    const maximum = track.scrollWidth - track.clientWidth;
    const position = animation ? target : track.scrollLeft;
    const canMove = direction > 0 ? position < maximum - 1 : position > 1;
    if (!direction) return;
    if (direction !== wheelDirection && canMove) move(direction);
    wheelDirection = direction;
    clearTimeout(wheelTimer);
    wheelTimer = setTimeout(() => { wheelDirection = 0; }, 160);
  }, { passive: false });

  // Use pointer capture after a mouse drag starts; touch keeps native swipe and pinch behavior.
  track.addEventListener('dragstart', event => event.preventDefault());
  track.addEventListener('pointerdown', event => {
    stopMotion();
    if (event.pointerType !== 'mouse' || event.button !== 0) return;
    drag = { id: event.pointerId, x: event.clientX, scroll: track.scrollLeft, moved: false };
  });
  track.addEventListener('pointermove', event => {
    if (!drag || event.pointerId !== drag.id) return;
    const distance = event.clientX - drag.x;
    if (!drag.moved && Math.abs(distance) < 6) return;
    if (!drag.moved) {
      drag.moved = true;
      track.setPointerCapture(event.pointerId);
      track.classList.add('is-dragging');
    }
    event.preventDefault();
    track.scrollLeft = drag.scroll - distance;
  });
  const finishDrag = event => {
    if (!drag || event.pointerId !== drag.id) return;
    suppressClick = drag.moved;
    if (track.hasPointerCapture(event.pointerId)) track.releasePointerCapture(event.pointerId);
    track.classList.remove('is-dragging');
    drag = null;
    setTimeout(() => { suppressClick = false; }, 0);
  };
  track.addEventListener('pointerleave', () => { if (drag && !drag.moved) drag = null; });
  track.addEventListener('pointerup', finishDrag);
  track.addEventListener('lostpointercapture', finishDrag);
  track.addEventListener('pointercancel', finishDrag);
  track.addEventListener('click', event => {
    if (suppressClick) {
      event.preventDefault();
      event.stopPropagation();
      return;
    }
    const link = event.target.closest('[data-gallery-photo]');
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || !dialog.showModal) return;
    event.preventDefault();
    const thumbnail = link.querySelector('img');
    const isVideo = link.hasAttribute('data-gallery-video');
    fullImage.hidden = isVideo;
    player.hidden = !isVideo;
    if (isVideo) {
      player.src = link.href;
      player.poster = thumbnail.src;
      player.setAttribute('aria-label', thumbnail.alt);
    } else {
      fullImage.src = link.href;
      fullImage.alt = thumbnail.alt;
    }
    caption.textContent = link.closest('figure').querySelector('figcaption')?.textContent || '';
    caption.hidden = !caption.textContent;
    dialog.showModal();
  }, true);
  dialog.querySelector('[data-gallery-close]').addEventListener('click', () => dialog.close());
  // Stop playback and release the video when the viewer closes, including Escape.
  dialog.addEventListener('close', () => {
    player.pause();
    player.removeAttribute('src');
    player.load();
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  scrollbar.hidden = false;
  updateControls();
});
