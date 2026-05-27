export default function ProgressBar({ progress, status, processed, total }) {
  return (
    <div className="progress-section">
      <div className="progress-info">
        <span>{status === 'completed' ? 'Completed' : status === 'completed_with_errors' ? 'Completed with errors' : 'Processing...'}</span>
        <span>{progress}%</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>
      {processed != null && total != null && (
        <div className="progress-info" style={{ marginTop: '0.5rem' }}>
          <small>{processed} of {total} files</small>
        </div>
      )}
    </div>
  );
}