import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAppContext } from '../context/AppContext';
import { uploadBatch } from '../api';
import useJobPolling from '../hooks/useJobPolling';
import { BookOpen, FolderPlus, FilePlus2 } from 'lucide-react';

export default function BookHeader({ onBack }) {
  const { t } = useTranslation();
  const { book, loadBookPages, pages, activePage } = useAppContext();
  const [newBookName, setNewBookName] = useState(book || '');
  const [jobId, setJobId] = useState(null);
  const [addJobRunning, setAddJobRunning] = useState(false);

  const handleAddComplete = async (job) => {
    if (job.status !== 'failed') {
      await loadBookPages(book);
    } else {
      alert(`${t('uploadError')}: ${job.errors[0] || ''}`);
    }
    setAddJobRunning(false);
    setJobId(null);
  };

  const { progress: addProgress } = useJobPolling(jobId, handleAddComplete);

  const handleLoadBook = (e) => {
    e.preventDefault();
    if (newBookName.trim()) loadBookPages(newBookName.trim());
  };

  const handleAddPages = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    for (const f of files) {
      if (!/^page_\d{3,}\.(jpg|jpeg|png|webp|bmp|tiff)$/i.test(f.name)) {
        alert(`${t('invalidFileName')}: "${f.name}"`);
        return;
      }
    }

    const formData = new FormData();
    formData.append('book_name', book);
    files.forEach((f) => formData.append('files', f));

    setAddJobRunning(true);

    try {
      const res = await uploadBatch(formData);
      setJobId(res.data.job_id);
    } catch (err) {
      alert(`${t('uploadError')}: ${err.response?.data?.detail || err.message}`);
      setAddJobRunning(false);
    }

    e.target.value = '';
  };

  const currentIndex = pages.findIndex((p) => p.page_number === activePage);

  return (
    <>
      <div className="book-header">
        <div className="book-toolbar">
          <div className="book-input-wrap">
            <input
              type="text"
              value={newBookName}
              onChange={(e) => setNewBookName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleLoadBook(e)}
              placeholder={t('enterBookName')}
              className="form-input"
            />
          </div>

          <div className="book-actions">
            <button className="btn btn-secondary toolbar-btn" onClick={handleLoadBook} type="button">
              <BookOpen size={18} strokeWidth={2} />
              <span>{t('load')}</span>
            </button>

            <button className="btn btn-secondary toolbar-btn" onClick={onBack} type="button">
              <FolderPlus size={18} strokeWidth={2} />
              <span>{t('new')}</span>
            </button>

            <label className="btn btn-secondary toolbar-btn toolbar-btn-wide">
              <FilePlus2 size={18} strokeWidth={2} />
              <span>{t('addPages')}</span>
              <input
                type="file"
                multiple
                accept="image/*"
                className="file-input"
                onChange={handleAddPages}
                disabled={addJobRunning}
              />
            </label>
          </div>
        </div>

        <div className="page-counter">
          <span>
            {t('page')} <strong>{currentIndex >= 0 ? currentIndex + 1 : 0}</strong> {t('of')} <strong>{pages.length}</strong>
          </span>
        </div>
      </div>

      {addJobRunning && (
        <div className="progress-section progress-section-inline">
          <div className="progress-info">
            <span>{t('addingPages')}</span>
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