import { useState } from 'react';

export default function NavigationBar({ onPrev, onNext, onGo, currentIndex, totalPages, activePage }) {
  const [inputVal, setInputVal] = useState(activePage || '');

  const handleGo = () => {
    const num = parseInt(inputVal, 10);
    if (num >= 1 && num <= totalPages) onGo(num);
    else setInputVal(activePage);
  };

  return (
    <div className="navigation-bar">
      <button className="nav-btn" onClick={onPrev} disabled={currentIndex <= 0}>
        ← Претходна
      </button>
      <div className="page-indicator">
        <input
          type="number"
          className="page-input"
          min="1"
          max={totalPages}
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleGo()}
          onBlur={handleGo}
        />
      </div>
      <button className="nav-btn" onClick={onNext} disabled={currentIndex >= totalPages - 1}>
        Следна →
      </button>
    </div>
  );
}