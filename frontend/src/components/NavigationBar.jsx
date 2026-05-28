import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

export default function NavigationBar({ onPrev, onNext, onGo, currentIndex, totalPages, activePage }) {
  const { t } = useTranslation();
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
        aria-label={t('previousPage')}
        title={t('previousPage')}
      >
        ←
      </button>

      <div className="page-indicator page-indicator-compact">
        <span className="page-pill">
          {t('page')} <strong>{currentIndex + 1}</strong> / {totalPages}
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
          aria-label={t('goToPage')}
        />
      </div>

      <button
        className="nav-btn nav-btn-icon"
        onClick={onNext}
        disabled={currentIndex >= totalPages - 1}
        aria-label={t('nextPage')}
        title={t('nextPage')}
      >
        →
      </button>
    </div>
  );
}