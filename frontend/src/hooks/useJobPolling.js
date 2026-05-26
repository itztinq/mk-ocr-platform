import { useState, useEffect, useRef } from 'react';
import { getJobStatus } from '../api';

export default function useJobPolling(jobId, onComplete) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('queued');
  const [processed, setProcessed] = useState(0);
  const [total, setTotal] = useState(0);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!jobId) return;
    const poll = async () => {
      try {
        const res = await getJobStatus(jobId);
        const job = res.data;
        setProgress(job.progress_percent);
        setStatus(job.status);
        setProcessed(job.processed_files);
        setTotal(job.total_files);
        if (['completed', 'completed_with_errors', 'failed'].includes(job.status)) {
          clearInterval(intervalRef.current);
          if (onComplete) onComplete(job);
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };
    poll();
    intervalRef.current = setInterval(poll, 1500);
    return () => clearInterval(intervalRef.current);
  }, [jobId, onComplete]);

  return { progress, status, processed, total };
}