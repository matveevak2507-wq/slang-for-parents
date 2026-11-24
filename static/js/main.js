document.addEventListener('DOMContentLoaded', () => {
  // Авто-скрытие flash
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // ---- Скролл-поведение верхней панели ----
  const topbar = document.getElementById('topbar');
  if (topbar) {
    let lastY = window.scrollY;

    const update = () => {
      const y = window.scrollY;
      if (y <= 5) {
        topbar.classList.add('topbar-visible');
        topbar.classList.remove('topbar-scrolled');
      } else if (y > lastY) {
        topbar.classList.remove('topbar-visible');
      } else {
        topbar.classList.add('topbar-visible');
        topbar.classList.add('topbar-scrolled');
      }
      lastY = y;
    };

    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  // ---- Выбор опции в викторине ----
  document.querySelectorAll('.option-radio').forEach(radio => {
    radio.addEventListener('change', () => {
      document.querySelectorAll('.option-btn').forEach(el =>
        el.classList.remove('option-selected'));
      const parent = radio.closest('.option-btn');
      if (parent) parent.classList.add('option-selected');
    });
  });
});