import { useState, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Upload, ImageUp, ScanText, FileEdit } from 'lucide-react';
import { uploadBatch } from '../api';
import { useAppContext } from '../context/AppContext';
import useJobPolling from '../hooks/useJobPolling';
import ProgressBar from './ProgressBar';

export default function UploadSection({ onBookProcessed }) {
  const { t } = useTranslation();
  const { loadBookPages } = useAppContext();
  const [bookName, setBookName] = useState('');
  const [files, setFiles] = useState([]);
  const [jobId, setJobId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleJobComplete = useCallback(async (job) => {
    if (job.status !== 'failed') {
      await loadBookPages(bookName);
      onBookProcessed();
    } else {
      alert(`${t('processingError')}: ${job.errors[0] || t('unknownError')}`);
    }
    setUploading(false);
    setJobId(null);
  }, [bookName, loadBookPages, onBookProcessed, t]);

  const { progress, status, processed, total } = useJobPolling(jobId, handleJobComplete);

  const handleFileSelect = (e) => {
    const selected = Array.from(e.target.files);
    setFiles((prev) => [...prev, ...selected]);
    e.target.value = '';
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (!bookName.trim()) return alert(t('enterBookNameAlert'));
    if (files.length === 0) return alert(t('selectAtLeastOneImage'));

    for (const f of files) {
      if (!/^page_\d{3,}\.(jpg|jpeg|png|webp|bmp|tiff)$/i.test(f.name)) {
        alert(`${t('invalidName')}: "${f.name}". ${t('mustBePageFormat')}`);
        return;
      }
    }

    const formData = new FormData();
    formData.append('book_name', bookName);
    files.forEach((f) => formData.append('files', f));

    setUploading(true);

    try {
      const res = await uploadBatch(formData);
      setJobId(res.data.job_id);
    } catch (err) {
      alert(`${t('uploadError')}: ${err.response?.data?.detail || err.message}`);
      setUploading(false);
    }
  };

  return (
    <>
      <section className="how-it-works">
        <div className="section-header">
          <h2>{t('howItWorks')}</h2>
          <p>{t('howItWorksText')}</p>
        </div>

        <div className="how-it-works-grid">
          <div className="how-step">
            <div className="how-step-icon">
              <Upload size={18} strokeWidth={2} />
            </div>
            <h3>{t('stepUpload')}</h3>
            <p>{t('stepUploadText')}</p>
          </div>

          <div className="how-step">
            <div className="how-step-icon">
              <ScanText size={18} strokeWidth={2} />
            </div>
            <h3>{t('stepReview')}</h3>
            <p>{t('stepReviewText')}</p>
          </div>

          <div className="how-step">
            <div className="how-step-icon">
              <FileEdit size={18} strokeWidth={2} />
            </div>
            <h3>{t('stepCorrect')}</h3>
            <p>{t('stepCorrectText')}</p>
          </div>
        </div>
      </section>

      <section className="upload-section">
        <div className="section-header">
          <h2 className="section-title-with-icon">
            <Upload size={20} strokeWidth={2} />
            <span>{t('uploadImages')}</span>
          </h2>
          <p>{t('uploadSubtitle')}</p>
        </div>

        <div className="upload-form">
          <div className="form-group">
            <label>{t('bookName')}</label>
            <input
              type="text"
              value={bookName}
              onChange={(e) => setBookName(e.target.value)}
              placeholder={t('bookNameExample')}
              className="form-input"
              disabled={uploading}
            />
          </div>

          <div className="form-group">
            <div
              className="upload-area"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const droppedFiles = Array.from(e.dataTransfer.files);
                setFiles((prev) => [...prev, ...droppedFiles]);
              }}
            >
              <span className="upload-icon">
                <ImageUp size={40} strokeWidth={1.8} />
              </span>
              <span className="upload-title">{t('clickOrDrag')}</span><br/>
              <small className="upload-hint">{t('fileHint')}</small>
            </div>

            <input
              type="file"
              ref={fileInputRef}
              multiple
              accept="image/*"
              className="file-input"
              onChange={handleFileSelect}
            />
          </div>

          <div className="selected-files">
            {files.map((f, i) => (
              <span key={i} className="file-badge">
                {f.name}
                <span className="remove-file" onClick={() => removeFile(i)}>×</span>
              </span>
            ))}
          </div>

          <div className="upload-actions">
            <button
              className="btn btn-primary"
              onClick={handleUpload}
              disabled={uploading}
              type="button"
            >
              {uploading ? t('uploading') : t('startOcr')}
            </button>

            <button
              className="btn btn-secondary"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              type="button"
            >
              {t('addMoreImages')}
            </button>
          </div>
        </div>

        {jobId && (
          <ProgressBar progress={progress} status={status} processed={processed} total={total} />
        )}
      </section>
    </>
  );
}