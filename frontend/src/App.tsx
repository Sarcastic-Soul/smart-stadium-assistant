import { useState, useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import Chat from './components/Chat';
import Map from './components/Map';
import Dashboard from './components/Dashboard';

type Tab = 'chat' | 'map' | 'dashboard';

function App() {
  const { t, i18n } = useTranslation();
  const [activeTab, setActiveTab] = useState<Tab>('chat');

  const [userRole, setUserRole] = useState<string>('fan');

  const changeLanguage = useCallback((lng: string) => {
    i18n.changeLanguage(lng);
  }, [i18n]);

  useEffect(() => {
    document.documentElement.lang = i18n.language;
  }, [i18n.language]);

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'chat', label: t('nav.chat'), icon: '💬' },
    { id: 'map', label: t('nav.map'), icon: '🗺️' },
    { id: 'dashboard', label: t('nav.dashboard'), icon: '📊' },
  ];

  return (
    <div className="app">
      <a href="#main-content" className="skip-link" id="skip-link">
        {t('accessibility.skipToContent')}
      </a>

      <header className="app-header" role="banner">
        <div className="app-logo">
          <div className="app-logo-icon" aria-hidden="true">⚽</div>
          <div>
            <h1>{t('app.title')}</h1>
            <div className="subtitle">{t('app.subtitle')}</div>
          </div>
        </div>

        <div className="header-controls">
          <nav className="nav-tabs" role="tablist" aria-label="Main navigation">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                id={`tab-${tab.id}`}
                role="tab"
                aria-selected={activeTab === tab.id}
                aria-controls={`panel-${tab.id}`}
                className={`nav-tab${activeTab === tab.id ? ' active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
                tabIndex={activeTab === tab.id ? 0 : -1}
              >
                <span className="tab-icon" aria-hidden="true">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>

          <select
            className="role-select"
            id="role-selector"
            aria-label="Select User Role"
            value={userRole}
            onChange={(e) => setUserRole(e.target.value)}
            title="Persona"
          >
            <option value="fan">Fan</option>
            <option value="staff">Staff</option>
            <option value="volunteer">Volunteer</option>
            <option value="organizer">Organizer</option>
          </select>

          <select
            className="lang-select"
            id="language-selector"
            aria-label={t('accessibility.languageSelect')}
            value={i18n.language}
            onChange={(e) => changeLanguage(e.target.value)}
          >
            <option value="en">🇬🇧 EN</option>
            <option value="es">🇪🇸 ES</option>
            <option value="fr">🇫🇷 FR</option>
            <option value="de">🇩🇪 DE</option>
          </select>
        </div>
      </header>

      <main className="app-main" id="main-content" role="main">
        {activeTab === 'chat' && (
          <div id="panel-chat" role="tabpanel" aria-labelledby="tab-chat">
            <Chat language={i18n.language} role={userRole} />
          </div>
        )}
        {activeTab === 'map' && (
          <div id="panel-map" role="tabpanel" aria-labelledby="tab-map">
            <Map />
          </div>
        )}
        {activeTab === 'dashboard' && (
          <div id="panel-dashboard" role="tabpanel" aria-labelledby="tab-dashboard">
            <Dashboard />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
