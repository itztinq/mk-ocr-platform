import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Clock, Loader2, Trash2, Trash } from 'lucide-react';
import { getJobHistory, deleteJob, clearJobHistory } from '../api';

const STATUS_LABELS = {
  queued: 'statusQueued',
  running: 'statusRunning',
  completed: 'statusCompleted',
  completed_with_errors: 'statusCompletedWithErrors',
  failed: 'statusFailed',
};

function formatDate(isoString) {
  const d = new Date(isoString);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export default function JobHistory({ onLoadBook }) {
  const { t } = useTranslation();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;

    const fetch = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await getJobHistory();
        if (!cancelled) setJobs(res.data.jobs);
      } catch (err) {
        if (!cancelled) setError(t('historyLoadError'));
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetch();
    return () => { cancelled = true; };
  }, [open, t]);

  const handleDeleteJob = useCallback(async (jobId) => {
    if (!window.confirm('Delete this job from history?')) return;
    try {
      await deleteJob(jobId);
      setJobs((prev) => prev.filter((j) => j.job_id !== jobId));
    } catch {
      alert('Failed to delete job');
    }
  }, []);

  const handleClearAll = useCallback(async () => {
    if (!window.confirm('Delete all scan history?')) return;
    try {
      await clearJobHistory();
      setJobs([]);
    } catch {
      alert('Failed to clear history');
    }
  }, []);

  return (
    <section className="history-section">
      <button
        className="history-toggle"
        onClick={() => setOpen((prev) => !prev)}
        type="button"
      >
        <Clock size={18} strokeWidth={2} />
        <span>{t('scanHistory')}</span>
        <span className={`history-chevron ${open ? 'open' : ''}`}>▸</span>
      </button>

      {open && (
        <div className="history-body">
          {loading && (
            <div className="history-loading">
              <Loader2 size={20} className="spin" />
            </div>
          )}

          {error && <p className="history-error">{error}</p>}

          {!loading && !error && jobs.length === 0 && (
            <p className="history-empty">{t('scanHistoryEmpty')}</p>
          )}

          {!loading && !error && jobs.length > 0 && (
            <div className="history-list">
              <div className="history-list-header">
                <span className="history-count">{jobs.length} jobs</span>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={handleClearAll}
                  type="button"
                >
                  <Trash size={14} strokeWidth={2} />
                  <span>Clear all</span>
                </button>
              </div>
              {jobs.map((job) => (
                <div key={job.job_id} className="history-item">
                  <div className="history-item-info">
                    <span className="history-book-name">{job.book_name}</span>
                    <span className={`history-status history-status--${job.status}`}>
                      {t(STATUS_LABELS[job.status] || job.status)}
                    </span>
                    <span className="history-date">{formatDate(job.created_at)}</span>
                  </div>
                  <div className="history-item-actions">
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => onLoadBook(job.book_name)}
                      type="button"
                    >
                      {t('loadBook')}
                    </button>
                    <button
                      className="btn btn-icon btn-sm"
                      onClick={() => handleDeleteJob(job.job_id)}
                      type="button"
                      title="Delete"
                    >
                      <Trash2 size={14} strokeWidth={2} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
