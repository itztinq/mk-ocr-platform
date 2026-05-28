import { useTranslation } from 'react-i18next';

export default function ProgressBar({ progress, status, processed, total }) {
  const { t } = useTranslation();

  return (
    <div className="progress-section">
      <div className="progress-info">
        <span>
          {status === 'completed'
            ? t('completed')
            : status === 'completed_with_errors'
              ? t('completedWithErrors')
              : t('processing')}
        </span>
        <span>{progress}%</span>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>

      {processed != null && total != null && (
        <div className="progress-info" style={{ marginTop: '0.5rem' }}>
          <small>{processed} {t('of')} {total} {t('filesCount')}</small>
        </div>
      )}
    </div>
  );
}