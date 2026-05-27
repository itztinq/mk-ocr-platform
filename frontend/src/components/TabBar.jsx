export default function TabBar({ activeTab, onTabChange }) {
  const tabs = [
    { key: 'cleaned', label: 'Cleaned' },
    { key: 'raw', label: 'Raw OCR' },
    { key: 'corrected', label: 'Corrected' },
  ];

  return (
    <div className="tab-bar">
      {tabs.map(tab => (
        <button
          key={tab.key}
          className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
          onClick={() => onTabChange(tab.key)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}