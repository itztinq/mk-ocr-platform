import { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { getPageDetail } from '../api';

export default function ImageViewer() {
  const { book, activePage, setPageTexts, loadingPage } = useAppContext();
  const [imageUrl, setImageUrl] = useState('');
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!book || !activePage) return;
    let cancelled = false;
    setError(false);
    getPageDetail(book, activePage)
      .then(page => {
        if (cancelled) return;
        if (page.page_image_url) {
            setImageUrl('http://127.0.0.1:8000' + page.page_image_url);
        } else {
            setImageUrl('');
            setError(true);
        }
      })
      .catch(() => { if (!cancelled) setError(true); });
    return () => { cancelled = true; };
  }, [book, activePage]);

  if (loadingPage) {
    return (
      <div className="image-container">
        <div className="image-placeholder">
          <span className="placeholder-icon">⏳</span>
          <span>Вчитувам...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="image-container">
      {imageUrl ? (
        <img src={imageUrl} alt="Страница" className="preview-image" />
      ) : (
        <div className="image-placeholder">
          <span className="placeholder-icon">🖼️</span>
          <span>{error ? 'Грешка при вчитување' : 'Сликата ќе се прикаже овде'}</span>
        </div>
      )}
    </div>
  );
}