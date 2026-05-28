import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAppContext } from '../context/AppContext';
import { downloadBookTxtApi } from '../api';
import TabBar from './TabBar';

export default function TextEditor() {
  const { t } = useTranslation();
  const {
    book,
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

  const handleDownloadPage = () => {
    const text = pageTexts[activeTab] || '';
    if (!text || !activePage) return;

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `page_${String(activePage).padStart(3, '0')}_${activeTab}.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const handleDownloadBook = async () => {
    if (!book) return;

    try {
      const response = await downloadBookTxtApi(book);
      const url = URL.createObjectURL(response.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${book}_corrected.txt`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      let errorMessage = err.message;

      if (err.response?.data instanceof Blob) {
        try {
          const text = await err.response.data.text();
          const parsed = JSON.parse(text);
          errorMessage = parsed.detail || err.message;
        } catch {
          errorMessage = err.message;
        }
      } else {
        errorMessage = err.response?.data?.detail || err.message;
      }

      setSaveStatus({
        type: 'error',
        message: `${t('uploadError')}: ${errorMessage}`,
      });
      setTimeout(() => setSaveStatus(null), 3000);
    }
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

          <button className="btn btn-secondary" onClick={handleDownloadPage} type="button">
            {t('downloadPage')}
          </button>

          <button className="btn btn-secondary" onClick={handleDownloadBook} type="button">
            {t('downloadBook')}
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