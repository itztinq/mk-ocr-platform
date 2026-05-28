import { useEffect, useState } from 'react';
import { Languages, Menu, Moon, ScanText, Sun, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { AppProvider } from './context/AppContext';
import UploadSection from './components/UploadSection';
import EditorSection from './components/EditorSection';
import './App.css';

function getInitialTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light' || savedTheme === 'dark') {
    return savedTheme;
  }
  return 'dark';
}

export default function App() {
  const [showEditor, setShowEditor] = useState(false);
  const [theme, setTheme] = useState(getInitialTheme);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { t, i18n } = useTranslation();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setMobileMenuOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === 'en' ? 'mk' : 'en');
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <AppProvider>
      <header className="app-header">
        <div className="header-content">
          <div className="header-top-row">
            <h1 className="app-title">
              <ScanText size={28} strokeWidth={2.2} />
              <span>{t('appTitle')}</span>
            </h1>

            <div className="header-actions desktop-actions">
              <button
                className="lang-toggle"
                onClick={toggleLanguage}
                type="button"
                aria-label={i18n.language === 'en' ? t('switchToMacedonian') : t('switchToEnglish')}
                title={i18n.language === 'en' ? t('switchToMacedonian') : t('switchToEnglish')}
              >
                <Languages size={18} strokeWidth={2} />
                <span className="lang-toggle-text">
                  {i18n.language === 'en' ? t('macedonian') : t('english')}
                </span>
              </button>

              <button
                className="theme-toggle"
                onClick={toggleTheme}
                type="button"
                aria-label={theme === 'dark' ? t('switchToLightMode') : t('switchToDarkMode')}
                title={theme === 'dark' ? t('switchToLightMode') : t('switchToDarkMode')}
              >
                {theme === 'dark' ? <Sun size={18} strokeWidth={2} /> : <Moon size={18} strokeWidth={2} />}
                <span className="theme-toggle-text">
                  {theme === 'dark' ? t('lightMode') : t('darkMode')}
                </span>
              </button>
            </div>

            <div className="mobile-menu-wrap">
              <button
                className="menu-toggle"
                type="button"
                onClick={() => setMobileMenuOpen((prev) => !prev)}
                aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
                title={mobileMenuOpen ? 'Close menu' : 'Open menu'}
                aria-expanded={mobileMenuOpen}
              >
                {mobileMenuOpen ? <X size={20} strokeWidth={2.2} /> : <Menu size={20} strokeWidth={2.2} />}
              </button>

              {mobileMenuOpen && (
                <div className="mobile-menu-panel">
                  <button
                    className="mobile-menu-action"
                    onClick={() => {
                      toggleLanguage();
                      closeMobileMenu();
                    }}
                    type="button"
                  >
                    <Languages size={18} strokeWidth={2} />
                    <span>{i18n.language === 'en' ? t('MK') : t('EN')}</span>
                  </button>

                  <button
                    className="mobile-menu-action"
                    onClick={() => {
                      toggleTheme();
                      closeMobileMenu();
                    }}
                    type="button"
                  >
                    {theme === 'dark' ? <Sun size={18} strokeWidth={2} /> : <Moon size={18} strokeWidth={2} />}
                    <span>{theme === 'dark' ? t('Light') : t('Dark')}</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          <p className="app-subtitle">{t('appSubtitle')}</p>
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
        <p>{t('footerTitle')}</p>
      </footer>
    </AppProvider>
  );
}