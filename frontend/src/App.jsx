import { useState } from 'react';
import { ScanText } from 'lucide-react';
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
            <ScanText size={28} strokeWidth={2.2} />
            <span>Macedonian OCR</span>
          </h1>
          <p className="app-subtitle">Convert scanned documents, screenshots, and images in Macedonian language into editable text formats.</p>
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