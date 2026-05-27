import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { getBookPages, getPageDetail, saveCorrectedTextApi } from '../api';

const AppContext = createContext();

export const useAppContext = () => useContext(AppContext);

export const AppProvider = ({ children }) => {
  const [book, setBook] = useState(null);
  const [pages, setPages] = useState([]);
  const [activePage, setActivePage] = useState(null);
  const [pageTexts, setPageTexts] = useState({ raw: '', cleaned: '', corrected: '' });
  const [activeTab, setActiveTab] = useState('cleaned');
  const [loadingPage, setLoadingPage] = useState(false);

  const loadBookPages = useCallback(async (bookName) => {
    const data = await getBookPages(bookName);
    setBook(bookName);
    setPages(data.pages);
    if (data.pages.length) {
      setActivePage(data.pages[0].page_number);
    } else {
      setActivePage(null);
    }
  }, []);

  const loadPageDetail = useCallback(async (pageNumber) => {
    if (!book) return;
    setLoadingPage(true);
    try {
      const page = await getPageDetail(book, pageNumber);
      const texts = {
        raw: page.raw_text?.content || '',
        cleaned: page.cleaned_text?.content || '',
        corrected: page.corrected_text?.content || '',
      };

      if (!page.corrected_text?.exists && page.cleaned_text?.exists) {
        texts.corrected = page.cleaned_text.content;
      }
      setPageTexts(texts);

      if (page.cleaned_text?.exists) setActiveTab('cleaned');
      else if (page.raw_text?.exists) setActiveTab('raw');
      else setActiveTab('corrected');
    } finally {
      setLoadingPage(false);
    }
  }, [book]);

  useEffect(() => {
    if (activePage) {
      loadPageDetail(activePage);
    }
  }, [activePage, loadPageDetail]);

  const updatePageText = (text) => {
    setPageTexts(prev => ({ ...prev, corrected: text }));
  };

  const saveCorrectedText = async () => {
    if (!book || !activePage) return;
    await saveCorrectedTextApi(book, activePage, pageTexts.corrected);
    await loadBookPages(book);
  };

  return (
    <AppContext.Provider value={{
      book, setBook,
      pages, setPages,
      activePage, setActivePage,
      pageTexts, setPageTexts: updatePageText,
      activeTab, setActiveTab,
      loadingPage,
      loadBookPages,
      loadPageDetail,
      saveCorrectedText,
    }}>
      {children}
    </AppContext.Provider>
  );
};