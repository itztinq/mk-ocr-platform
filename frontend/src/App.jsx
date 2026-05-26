import { useState } from 'react';
import { AppProvider } from './context/AppContext';
import UploadSection from './components/UploadSection';
import EditorSection from './components/EditorSection';
import './App.css';

function App() {
  const [showEditor, setShowEditor] = useState(false);

  return (
    <AppProvider>
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            <span className="title-icon">📖</span>
            Macedonian OCR
          </h1>
          <p className="app-subtitle">Препознај македонски текст од слики</p>
        </div>
      </header>
      <main className="app-container">
        {showEditor ? (
          <EditorSection onBack={() => setShowEditor(false)} />
        ) : (
          <UploadSection onBookProcessed={() => setShowEditor(true)} />
        )}
      </main>
      <footer className="app-footer">
        <p>Macedonian OCR Platform</p>
      </footer>
    </AppProvider>
  );
}

export default App;