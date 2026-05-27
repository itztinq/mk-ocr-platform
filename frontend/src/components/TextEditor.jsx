import { useEffect, useState } from 'react';
import { useAppContext } from '../context/AppContext';
import TabBar from './TabBar';

export default function TextEditor() {
  const { pageTexts, setPageTexts, activeTab, setActiveTab, activePage, book, saveCorrectedText, loadingPage } = useAppContext();
  const [saveStatus, setSaveStatus] = useState(null); // { type: 'success'/'error', message }

  const isEditable = activeTab === 'corrected';

  const handleTextChange = (e) => {
    if (!isEditable) return;
    setPageTexts(e.target.value);
  };

  const handleCopy = () => {
    const text = pageTexts[activeTab] || '';
    navigator.clipboard.writeText(text);
    setSaveStatus({ type: 'success', message: 'Copied!' });
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
      setSaveStatus({ type: 'success', message: 'Saved' });
    } catch (err) {
      setSaveStatus({ type: 'error', message: 'Error: ' + (err.response?.data?.detail || err.message) });
    }
    setTimeout(() => setSaveStatus(null), 3000);
  };

  if (!activePage) return <div className="editor-container"><textarea readOnly placeholder="Select page" /></div>;

  return (
    <>
      <TabBar activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="editor-container">
        <textarea
          id="textEditor"
          value={pageTexts[activeTab] || ''}
          onChange={handleTextChange}
          readOnly={!isEditable}
          placeholder="OCR text will appear here..."
          disabled={loadingPage}
        />
        <div className="editor-toolbar">
          <button className="btn btn-secondary" onClick={handleCopy} type="button">
            Copy
          </button>

          <button className="btn btn-secondary" onClick={handleDownload} type="button">
            Download
          </button>

          {isEditable && (
            <button className="btn btn-success" onClick={handleSave} type="button">
              Save corrections
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