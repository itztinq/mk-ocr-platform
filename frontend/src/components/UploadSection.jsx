import { useState, useRef, useCallback } from 'react';
import { Upload, ImageUp, ScanText, FileEdit, Download } from 'lucide-react';
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
      alert('Error during processing: ' + (job.errors[0] || 'Unknown error'));
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
    if (!bookName.trim()) return alert('Enter book name');
    if (files.length === 0) return alert('Select at least one image');

    for (let f of files) {
      if (!/^page_\d{3,}\.(jpg|jpeg|png|webp|bmp|tiff)$/i.test(f.name)) {
        alert(`Invalid name: "${f.name}". Must be page_001.jpg etc.`);
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
      alert('Error: ' + (err.response?.data?.detail || err.message));
      setUploading(false);
    }
  };

  return (
    <>
      <section className="how-it-works">
        <div className="section-header">
          <h2>How it works</h2>
          <p>
            Upload scanned pages, review the extracted text, correct any OCR errors,
            and download the final cleaned version.
          </p>
        </div>

        <div className="how-it-works-grid">
          <div className="how-step">
            <div className="how-step-icon">
              <Upload size={18} strokeWidth={2} />
            </div>
            <h3>Upload pages</h3>
            <p>Add one or more scanned images with the correct page filename format.</p>
          </div>

          <div className="how-step">
            <div className="how-step-icon">
              <ScanText size={18} strokeWidth={2} />
            </div>
            <h3>Review OCR</h3>
            <p>Open each page, compare the OCR text with the scanned image, and inspect the result.</p>
          </div>

          <div className="how-step">
            <div className="how-step-icon">
              <FileEdit size={18} strokeWidth={2} />
            </div>
            <h3>Correct and export</h3>
            <p>Edit mistakes, save corrections, then copy or download the cleaned text.</p>
          </div>
        </div>
      </section>

      <section className="upload-section">
        <div className="section-header">
          <h2 className="section-title-with-icon">
            <Upload size={20} strokeWidth={2} />
            <span>Upload Images</span>
          </h2>
          <p>Select multiple images and start OCR processing</p>
        </div>

        <div className="upload-form">
          <div className="form-group">
            <label>Book Name</label>
            <input
              type="text"
              value={bookName}
              onChange={(e) => setBookName(e.target.value)}
              placeholder="e.g., macedonian-novel"
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
              <span className="upload-icon">
                <ImageUp size={40} strokeWidth={1.8} />
              </span>
              <span className="upload-title">Click or drag images here</span><br/>
              <small className="upload-hint">page_001.jpg, page_002.png...</small>
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
              {uploading ? 'Uploading...' : 'Start OCR'}
            </button>

            <button
              className="btn btn-secondary"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              type="button"
            >
              Add More Images
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