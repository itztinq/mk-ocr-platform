import { useEffect, useState } from 'react';
import { Moon, ScanText, Sun } from 'lucide-react';
import { AppProvider } from './context/AppContext';
import UploadSection from './components/UploadSection';
import EditorSection from './components/EditorSection';
import './App.css';

function getInitialTheme() {
  const savedTheme = localStorage.getItem('theme');

  if (savedTheme === 'light' || savedTheme === 'dark') {
    return savedTheme;
  }

  return wwindow.matchMedia('(prefers-color-scheme: dark)');
}

function App() {
  const [showEditor, setShowEditor] = useState(false);
  const [theme, setTheme] = useState(getInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <AppProvider>
      <header className="app-header">
        <div className="header-content">
          <div className="header-top-row">
            <h1 className="app-title">
              <ScanText size={28} strokeWidth={2.2} />
              <span>Macedonian OCR</span>
            </h1>

            <button
              className="theme-toggle"
              onClick={toggleTheme}
              type="button"
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? <Sun size={18} strokeWidth={2} /> : <Moon size={18} strokeWidth={2} />}
              <span className="theme-toggle-text">
                {theme === 'dark' ? 'Light mode' : 'Dark mode'}
              </span>
            </button>
          </div>

          <p className="app-subtitle">
            Convert scanned documents, screenshots, and images in Macedonian language into editable text formats.
          </p>
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