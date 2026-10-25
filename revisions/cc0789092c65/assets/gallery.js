// Enhance the Lab photo strip; links and native scrolling work without JavaScript.
document.querySelectorAll('[data-gallery]').forEach(gallery => {
  const track = gallery.querySelector('.gallery-track');
  const previous = gallery.querySelector('[data-gallery-previous]');
  const next = gallery.querySelector('[data-gallery-next]');
  const dialog = gallery.querySelector('dialog');
  const fullImage = dialog.querySelector('[data-gallery-full]');
  const caption = dialog.querySelector('[data-gallery-caption]');
  let drag = null;
  let suppressClick = false;

  const updateControls = () => {
    previous.disabled = track.scrollLeft <= 1;
    next.disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 1;
  };
  const move = direction => {
    const item = track.querySelector('.gallery-item');
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    track.scrollBy({
      left: direction * (item.getBoundingClientRect().width + gap),
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'
    });
  };
  previous.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  track.addEventListener('scroll', updateControls, { passive: true });
  new ResizeObserver(updateControls).observe(track);
  track.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      move(event.key === 'ArrowRight' ? 1 : -1);
    }
  });

  // Translate a vertical mouse wheel only while the strip can scroll in that direction.
  track.addEventListener('wheel', event => {
    if (event.ctrlKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
    const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? track.clientWidth : 1;
    const delta = event.deltaY * unit;
    const maximum = track.scrollWidth - track.clientWidth;
    if ((delta > 0 && track.scrollLeft < maximum - 1) || (delta < 0 && track.scrollLeft > 1)) {
      event.preventDefault();
      track.scrollLeft += delta;
    }
  }, { passive: false });

  // Use pointer capture after a mouse drag starts; touch keeps native swipe and pinch behavior.
  track.addEventListener('dragstart', event => event.preventDefault());
  track.addEventListener('pointerdown', event => {
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
    fullImage.src = link.href;
    fullImage.alt = thumbnail.alt;
    caption.textContent = link.closest('figure').querySelector('figcaption')?.textContent || '';
    caption.hidden = !caption.textContent;
    dialog.showModal();
  }, true);
  dialog.querySelector('[data-gallery-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  previous.hidden = false;
  next.hidden = false;
  updateControls();
});
