export default function ProgressBar({ progress, status, processed, total }) {
  return (
    <div className="progress-section">
      <div className="progress-info">
        <span>{status === 'completed' ? 'Завршено' : status === 'completed_with_errors' ? 'Завршено со грешки' : 'Обработувам...'}</span>
        <span>{progress}%</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>
      {processed != null && total != null && (
        <div className="progress-info" style={{ marginTop: '0.5rem' }}>
          <small>{processed} од {total} датотеки</small>
        </div>
      )}
    </div>
  );
}