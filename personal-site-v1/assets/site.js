(() => {
  const filters = [...document.querySelectorAll('[data-filter]')];
  const rows = [...document.querySelectorAll('[data-tags]')];
  if (filters.length && rows.length) {
    filters.forEach((button) => {
      button.addEventListener('click', () => {
        const selected = button.dataset.filter;
        filters.forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
        rows.forEach((row) => {
          const tags = (row.dataset.tags || '').split(' ');
          row.hidden = selected !== 'all' && !tags.includes(selected);
        });
      });
    });
  }

  const progress = document.querySelector('[data-reading-progress]');
  if (progress) {
    const updateProgress = () => {
      const root = document.documentElement;
      const max = root.scrollHeight - window.innerHeight;
      const ratio = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      progress.style.width = `${ratio * 100}%`;
    };
    updateProgress();
    addEventListener('scroll', updateProgress, { passive: true });
    addEventListener('resize', updateProgress);
  }

  const shareButton = document.querySelector('[data-share]');
  if (shareButton) {
    shareButton.addEventListener('click', async () => {
      const original = shareButton.textContent;
      try {
        if (navigator.share) {
          await navigator.share({ title: document.title, url: location.href });
        } else if (navigator.clipboard) {
          await navigator.clipboard.writeText(location.href);
          shareButton.textContent = '链接已复制';
          setTimeout(() => { shareButton.textContent = original; }, 1600);
        }
      } catch (error) {
        if (error?.name !== 'AbortError') console.warn('Share unavailable', error);
      }
    });
  }
})();
