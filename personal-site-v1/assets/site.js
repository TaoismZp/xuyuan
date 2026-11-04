(() => {
  const filters = [...document.querySelectorAll('[data-filter]')];
  const rows = [...document.querySelectorAll('[data-tags]')];

  if (filters.length && rows.length) {
    const applyFilter = (selected, updateUrl = true) => {
      const valid = filters.some((button) => button.dataset.filter === selected);
      const value = valid ? selected : 'all';

      filters.forEach((button) => {
        button.setAttribute('aria-pressed', String(button.dataset.filter === value));
      });

      rows.forEach((row) => {
        const tags = (row.dataset.tags || '').split(' ').filter(Boolean);
        row.hidden = value !== 'all' && !tags.includes(value);
      });

      if (updateUrl) {
        const url = new URL(location.href);
        if (value === 'all') url.searchParams.delete('tag');
        else url.searchParams.set('tag', value);
        history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`);
      }
    };

    const initial = new URL(location.href).searchParams.get('tag') || 'all';
    applyFilter(initial, false);

    filters.forEach((button) => {
      button.addEventListener('click', () => applyFilter(button.dataset.filter || 'all'));
    });
  }

  const progress = document.querySelector('[data-reading-progress]');
  if (progress) {
    let queued = false;
    const updateProgress = () => {
      queued = false;
      const root = document.documentElement;
      const max = root.scrollHeight - window.innerHeight;
      const ratio = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      progress.style.transform = `scaleX(${ratio})`;
      progress.dataset.progress = String(Math.round(ratio * 100));
    };
    const requestUpdate = () => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(updateProgress);
    };
    updateProgress();
    addEventListener('scroll', requestUpdate, { passive: true });
    addEventListener('resize', requestUpdate);
  }

  const outlineLinks = [...document.querySelectorAll('[data-outline-link]')];
  if (outlineLinks.length) {
    const headings = [...new Set(outlineLinks.map(link => link.hash.slice(1)))]
      .map(id => document.getElementById(id))
      .filter(Boolean);
    let currentSection = '';
    let queued = false;
    const updateCurrentSection = () => {
      queued = false;
      let active = '';
      for (const heading of headings) {
        if (heading.getBoundingClientRect().top <= window.innerHeight * .32) active = heading.id;
      }
      if (currentSection === active) return;
      currentSection = active;
      for (const link of outlineLinks) {
        if (link.hash === '#' + active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      }
    };
    const queueOutlineUpdate = () => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(updateCurrentSection);
    };
    updateCurrentSection();
    addEventListener('scroll', queueOutlineUpdate, { passive: true });
    addEventListener('resize', queueOutlineUpdate);
    addEventListener('hashchange', queueOutlineUpdate);
    outlineLinks.forEach(link => link.addEventListener('click', () => {
      const disclosure = link.closest('details');
      if (disclosure) disclosure.open = false;
      queueOutlineUpdate();
    }));
  }

  const shareUrl = document.querySelector('link[rel="canonical"]')?.href || location.href;
  const shareButton = document.querySelector('[data-share]');
  const shareStatus = document.querySelector('[data-share-status]');
  if (shareButton) {
    shareButton.addEventListener('click', async () => {
      try {
        if (navigator.share) {
          await navigator.share({ title: document.title, url: shareUrl });
        } else if (navigator.clipboard) {
          await navigator.clipboard.writeText(shareUrl);
          if (shareStatus) shareStatus.textContent = '文章链接已复制。';
        } else if (shareStatus) {
          shareStatus.textContent = '当前浏览器不支持自动分享，请复制地址栏链接。';
        }
      } catch (error) {
        if (error?.name !== 'AbortError' && shareStatus) {
          shareStatus.textContent = '分享没有完成，请再试一次。';
        }
      }
    });
  }
})();
