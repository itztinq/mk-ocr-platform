import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAppContext } from '../context/AppContext';
import TabBar from './TabBar';

export default function TextEditor() {
  const { t } = useTranslation();
  const {
    pageTexts,
    setPageTexts,
    activeTab,
    setActiveTab,
    activePage,
    saveCorrectedText,
    loadingPage,
  } = useAppContext();

  const [saveStatus, setSaveStatus] = useState(null);
  const isEditable = activeTab === 'corrected';

  const handleTextChange = (e) => {
    if (!isEditable) return;
    setPageTexts(e.target.value);
  };

  const handleCopy = async () => {
    const text = pageTexts[activeTab] || '';
    await navigator.clipboard.writeText(text);
    setSaveStatus({ type: 'success', message: t('copied') });
    setTimeout(() => setSaveStatus(null), 2000);
  };

  const handleDownload = () => {
    const text = pageTexts[activeTab] || '';
    if (!text) return;

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `page_${String(activePage).padStart(3, '0')}_${activeTab}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleSave = async () => {
    try {
      await saveCorrectedText();
      setSaveStatus({ type: 'success', message: t('saved') });
    } catch (err) {
      setSaveStatus({
        type: 'error',
        message: `${t('uploadError')}: ${err.response?.data?.detail || err.message}`,
      });
    }
    setTimeout(() => setSaveStatus(null), 3000);
  };

  if (!activePage) {
    return (
      <div className="editor-container">
        <textarea readOnly placeholder={t('selectPage')} />
      </div>
    );
  }

  return (
    <>
      <TabBar activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="editor-container">
        <textarea
          id="textEditor"
          value={pageTexts[activeTab] || ''}
          onChange={handleTextChange}
          readOnly={!isEditable}
          placeholder={t('ocrTextPlaceholder')}
          disabled={loadingPage}
        />

        <div className="editor-toolbar">
          <button className="btn btn-secondary" onClick={handleCopy} type="button">
            {t('copy')}
          </button>

          <button className="btn btn-secondary" onClick={handleDownload} type="button">
            {t('download')}
          </button>

          {isEditable && (
            <button className="btn btn-success" onClick={handleSave} type="button">
              {t('saveCorrections')}
            </button>
          )}
        </div>

        {saveStatus && (
          <div className={`save-status ${saveStatus.type}`}>
            {saveStatus.message}
          </div>
        )}
      </div>
    </>
  );
}