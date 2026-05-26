import { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { uploadBatch } from '../api';
import useJobPolling from '../hooks/useJobPolling';

export default function BookHeader({ onBack }) {
  const { book, loadBookPages, pages, activePage } = useAppContext();
  const [newBookName, setNewBookName] = useState(book || '');
  const [addingFiles, setAddingFiles] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [addJobRunning, setAddJobRunning] = useState(false);

  const handleAddComplete = async (job) => {
    if (job.status !== 'failed') {
      await loadBookPages(book);
    } else {
      alert('Грешка: ' + (job.errors[0] || ''));
    }
    setAddJobRunning(false);
    setJobId(null);
    setAddingFiles(null);
  };

  const { progress: addProgress, status: addStatus, processed: addProcessed, total: addTotal } = useJobPolling(jobId, handleAddComplete);

  const handleLoadBook = (e) => {
    e.preventDefault();
    if (newBookName.trim()) loadBookPages(newBookName.trim());
  };

  const handleAddPages = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    for (let f of files) {
      if (!/^page_\d{3,}\.(jpg|jpeg|png|webp|bmp|tiff)$/i.test(f.name)) {
        alert(`Невалидно име: "${f.name}"`);
        return;
      }
    }
    const formData = new FormData();
    formData.append('book_name', book);
    files.forEach(f => formData.append('files', f));
    setAddingFiles(files);
    setAddJobRunning(true);
    try {
      const res = await uploadBatch(formData);
      setJobId(res.data.job_id);
    } catch (err) {
      alert('Грешка: ' + (err.response?.data?.detail || err.message));
      setAddJobRunning(false);
    }
    e.target.value = '';
  };

  const currentIndex = pages.findIndex(p => p.page_number === activePage);
  const pageCounter = activePage ? `${currentIndex + 1} / ${pages.length}` : '0 / 0';

  return (
    <>
      <div className="book-header">
        <div className="book-selector">
          <input
            type="text"
            value={newBookName}
            onChange={(e) => setNewBookName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLoadBook(e)}
            placeholder="Внеси име на книга"
            className="form-input"
          />
          <button className="btn btn-secondary" onClick={handleLoadBook}>📖 Вчитај</button>
          <button className="btn btn-secondary" onClick={onBack}>📤 Нова</button>
          <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
            📄 Додади страници
            <input
              type="file"
              multiple
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleAddPages}
              disabled={addJobRunning}
            />
          </label>
        </div>
        <div className="page-counter">
          <span>Страна <strong>{currentIndex + 1}</strong> од <strong>{pages.length}</strong></span>
        </div>
      </div>
      {addJobRunning && (
        <div className="progress-section" style={{ marginBottom: '1rem' }}>
          <div className="progress-info">
            <span>Додавам страници...</span>
            <span>{addProgress}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${addProgress}%` }}></div>
          </div>
        </div>
      )}
    </>
  );
}