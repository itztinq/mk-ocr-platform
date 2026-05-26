import { useAppContext } from '../context/AppContext';
import BookHeader from './BookHeader';
import PageThumbnails from './PageThumbnails';
import ImageViewer from './ImageViewer';
import TextEditor from './TextEditor';
import NavigationBar from './NavigationBar';
import useKeyboardNav from '../hooks/useKeyboardNav';
import { useCallback, useMemo } from 'react';

export default function EditorSection({ onBack }) {
  const { pages, activePage, setActivePage, book, loadingPage } = useAppContext();
  
  const currentIndex = useMemo(() => pages.findIndex(p => p.page_number === activePage), [pages, activePage]);
  const totalPages = pages.length;

  const goToPrev = useCallback(() => {
    if (currentIndex > 0) setActivePage(pages[currentIndex - 1].page_number);
  }, [currentIndex, pages, setActivePage]);

  const goToNext = useCallback(() => {
    if (currentIndex < totalPages - 1) setActivePage(pages[currentIndex + 1].page_number);
  }, [currentIndex, totalPages, pages, setActivePage]);

  const goToPage = useCallback((pageNum) => {
    const page = pages.find(p => p.page_number === pageNum);
    if (page) setActivePage(page.page_number);
  }, [pages, setActivePage]);

  useKeyboardNav(goToPrev, goToNext, loadingPage);

  return (
    <section className="editor-section">
      <BookHeader onBack={onBack} />
      <div className="editor-workspace">
        <div className="text-panel">
          <TextEditor />
        </div>
        <div className="image-panel">
          <ImageViewer />
          <NavigationBar
            onPrev={goToPrev}
            onNext={goToNext}
            onGo={goToPage}
            currentIndex={currentIndex}
            totalPages={totalPages}
            activePage={activePage}
          />
          <PageThumbnails />
        </div>
      </div>
    </section>
  );
}