import { useEffect } from 'react';

export default function useKeyboardNav(prev, next, disabled = false) {
  useEffect(() => {
    if (disabled) return;
    const handler = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prev && prev();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        next && next();
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [prev, next, disabled]);
}