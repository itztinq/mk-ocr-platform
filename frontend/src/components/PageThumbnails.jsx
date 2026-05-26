import { useEffect, useRef } from 'react';
import { useAppContext } from '../context/AppContext';

function getWindowIndices(total, activeIdx, windowSize = 9) {
  if (total <= windowSize) return Array.from({ length: total }, (_, i) => i);
  let start = activeIdx - Math.floor(windowSize / 2);
  let end = activeIdx + Math.floor(windowSize / 2);
  if (start < 0) { start = 0; end = windowSize - 1; }
  if (end >= total) { end = total - 1; start = end - windowSize + 1; }
  return Array.from({ length: end - start + 1 }, (_, i) => i + start);
}

export default function PageThumbnails() {
  const { pages, activePage, setActivePage } = useAppContext();
  const barRef = useRef(null);

  const activeIdx = pages.findIndex(p => p.page_number === activePage);
  const total = pages.length;
  const indices = getWindowIndices(total, activeIdx);

  useEffect(() => {
    if (barRef.current) {
      const activeEl = barRef.current.querySelector('.thumbnail-item.active');
      if (activeEl) {
        activeEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    }
  }, [activePage]);

  return (
    <div className="thumbnails-bar" ref={barRef}>
      {indices[0] > 0 && <div className="thumbnail-ellipsis">…</div>}
      {indices.map(idx => {
        const page = pages[idx];
        return (
          <div
            key={page.page_number}
            className={`thumbnail-item status-${page.status} ${activePage === page.page_number ? 'active' : ''}`}
            onClick={() => setActivePage(page.page_number)}
            title={`Страница ${page.page_number} (${page.status})`}
          >
            {page.page_number}
          </div>
        );
      })}
      {indices[indices.length - 1] < total - 1 && <div className="thumbnail-ellipsis">…</div>}
    </div>
  );
}