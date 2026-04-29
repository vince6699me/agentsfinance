import { useState } from 'react';
import { Sector, SECTORS, SectorInfo } from './components/SectorSelector';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Signals from './pages/Signals';
import Activity from './pages/Activity';

export default function App() {
  const [activeSector, setActiveSector] = useState<Sector>('forex');
  const [currentPage, setCurrentPage] = useState('dashboard');

  const handleSectorChange = (sector: Sector) => {
    setActiveSector(sector);
  };

  const currentSectorInfo = SECTORS.find((s: SectorInfo) => s.id === activeSector) as SectorInfo;

  const renderPage = () => {
    switch (currentPage) {
      case 'signals':
        return <Signals />;
      case 'activity':
        return <Activity />;
      case 'analytics':
        return <Analytics />;
      case 'dashboard':
      default:
        return (
          <Dashboard
            activeSector={activeSector}
            onSectorChange={handleSectorChange}
            currentSectorInfo={currentSectorInfo}
          />
        );
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          Agent<span>Finance</span>
        </div>
        <nav>
          <ul className="nav-menu">
            <li
              className={`nav-item ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              📊 Dashboard
            </li>
            <li
              className={`nav-item ${currentPage === 'signals' ? 'active' : ''}`}
              onClick={() => setCurrentPage('signals')}
            >
              📈 Signals
            </li>
            <li
              className={`nav-item ${currentPage === 'trades' ? 'active' : ''}`}
              onClick={() => setCurrentPage('trades')}
            >
              💹 Trades
            </li>
            <li
              className={`nav-item ${currentPage === 'scanner' ? 'active' : ''}`}
              onClick={() => setCurrentPage('scanner')}
            >
              🔍 Scanner
            </li>
            <li
              className={`nav-item ${currentPage === 'analysis' ? 'active' : ''}`}
              onClick={() => setCurrentPage('analysis')}
            >
              🔬 Analysis
            </li>
            <li
              className={`nav-item ${currentPage === 'backtest' ? 'active' : ''}`}
              onClick={() => setCurrentPage('backtest')}
            >
              ⚙️ Backtest
            </li>
            <li
              className={`nav-item ${currentPage === 'analytics' ? 'active' : ''}`}
              onClick={() => setCurrentPage('analytics')}
            >
              📉 Analytics
            </li>
            <li
              className={`nav-item ${currentPage === 'activity' ? 'active' : ''}`}
              onClick={() => setCurrentPage('activity')}
            >
              📋 Activity
            </li>
            <li
              className={`nav-item ${currentPage === 'settings' ? 'active' : ''}`}
              onClick={() => setCurrentPage('settings')}
            >
              ⚙️ Settings
            </li>
          </ul>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}