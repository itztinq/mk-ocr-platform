import { useTranslation } from 'react-i18next';

export default function TabBar({ activeTab, onTabChange }) {
  const { t } = useTranslation();

  const tabs = [
    { key: 'cleaned', label: t('cleaned') },
    { key: 'raw', label: t('rawOcr') },
    { key: 'corrected', label: t('corrected') },
  ];

  return (
    <div className="tab-bar">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
          onClick={() => onTabChange(tab.key)}
          type="button"
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}