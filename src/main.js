'use strict';
const search = document.getElementById('article-search');
if (search) {
  const rows = Array.from(document.querySelectorAll('[data-article]'));
  const empty = document.getElementById('no-results');
  const count = document.getElementById('article-count');
  const status = document.getElementById('search-status');
  search.addEventListener('input', () => {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const row of rows) {
      row.hidden = !row.dataset.search.toLocaleLowerCase().includes(query);
      if (!row.hidden) visible++;
    }
    count.textContent = String(visible).padStart(2, '0');
    empty.hidden = visible !== 0 || !query;
    status.textContent = query ? `找到 ${visible} 篇文章` : '';
  });
}
