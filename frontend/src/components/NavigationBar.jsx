import { useEffect, useState } from 'react';

export default function NavigationBar({ onPrev, onNext, onGo, currentIndex, totalPages, activePage }) {
  const [inputVal, setInputVal] = useState(activePage || '');

  useEffect(() => {
    setInputVal(activePage || '');
  }, [activePage]);

  const handleGo = () => {
    const num = parseInt(inputVal, 10);
    if (num >= 1 && num <= totalPages) onGo(num);
    else setInputVal(activePage);
  };

  return (
    <div className="navigation-bar">
      <button
        className="nav-btn nav-btn-icon"
        onClick={onPrev}
        disabled={currentIndex <= 0}
        aria-label="Previous page"
        title="Previous page"
      >
        ←
      </button>

      <div className="page-indicator page-indicator-compact">
        <span className="page-pill">
          Page <strong>{currentIndex + 1}</strong> / {totalPages}
        </span>

        <input
          type="number"
          className="page-input"
          min="1"
          max={totalPages}
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleGo()}
          onBlur={handleGo}
          aria-label="Go to page"
        />
      </div>

      <button
        className="nav-btn nav-btn-icon"
        onClick={onNext}
        disabled={currentIndex >= totalPages - 1}
        aria-label="Next page"
        title="Next page"
      >
        →
      </button>
    </div>
  );
}