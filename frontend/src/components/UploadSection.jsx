import { useState, useRef, useCallback } from 'react';
import { uploadBatch } from '../api';
import { useAppContext } from '../context/AppContext';
import useJobPolling from '../hooks/useJobPolling';
import ProgressBar from './ProgressBar';

export default function UploadSection({ onBookProcessed }) {
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
      alert('Грешка при обработка: ' + (job.errors[0] || 'Непозната грешка'));
    }
    setUploading(false);
    setJobId(null);
  }, [bookName, loadBookPages, onBookProcessed]);

  const { progress, status, processed, total } = useJobPolling(jobId, handleJobComplete);

  const handleFileSelect = (e) => {
    const selected = Array.from(e.target.files);
    setFiles(prev => [...prev, ...selected]);
    e.target.value = '';
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (!bookName.trim()) return alert('Внеси име на книга');
    if (files.length === 0) return alert('Избери барем една слика');
    // валидација на имиња
    for (let f of files) {
      if (!/^page_\d{3,}\.(jpg|jpeg|png|webp|bmp|tiff)$/i.test(f.name)) {
        alert(`Невалидно име: "${f.name}". Мора да биде page_001.jpg и сл.`);
        return;
      }
    }
    const formData = new FormData();
    formData.append('book_name', bookName);
    files.forEach(f => formData.append('files', f));
    setUploading(true);
    try {
      const res = await uploadBatch(formData);
      setJobId(res.data.job_id);
    } catch (err) {
      alert('Грешка: ' + (err.response?.data?.detail || err.message));
      setUploading(false);
    }
  };

  return (
    <section className="upload-section">
      <div className="section-header">
        <h2>📤 Прикачи слики</h2>
        <p>Избери повеќе слики и започни OCR обработка</p>
      </div>
      <div className="upload-form">
        <div className="form-group">
          <label>Име на книга</label>
          <input
            type="text"
            value={bookName}
            onChange={(e) => setBookName(e.target.value)}
            placeholder="пр. македонски-роман"
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
              setFiles(prev => [...prev, ...droppedFiles]);
            }}
          >
            <span className="upload-icon">📁</span>
            <span>Кликни или повлечи слики овде</span>
            <small>page_001.jpg, page_002.png...</small>
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
          >
            {uploading ? '⏳ Испраќам...' : '🚀 Започни OCR'}
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            ➕ Додади уште слики
          </button>
        </div>
      </div>
      {jobId && (
        <ProgressBar progress={progress} status={status} processed={processed} total={total} />
      )}
    </section>
  );
}