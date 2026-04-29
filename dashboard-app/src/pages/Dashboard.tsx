import { useState, useEffect } from 'react';
import SectorSelector, { Sector, SectorInfo } from '../components/SectorSelector';

interface DashboardProps {
  activeSector: Sector;
  onSectorChange: (sector: Sector) => void;
  currentSectorInfo: SectorInfo;
}

// Mock data generators
const generateMockPrice = (base: number): { price: number; change: number } => {
  const variation = (Math.random() - 0.5) * base * 0.02;
  const price = base + variation;
  const change = (Math.random() - 0.5) * 4;
  return { price: Number(price.toFixed(2)), change: Number(change.toFixed(2)) };
};

// Mock prices for demo (would come from API in real app)
const MOCK_PRICES: Record<string, number> = {
  // Forex
  EURUSD: 1.0850, GBPUSD: 1.2650, USDJPY: 149.50, USDCHF: 0.8850, AUDUSD: 0.6550,
  USDCAD: 1.3550, NZDUSD: 0.6050, EURGBP: 0.8580, EURJPY: 162.25, GBPJPY: 189.20,
  AUDJPY: 97.95, CADJPY: 110.30, CHFJPY: 168.90, EURAUD: 1.6550, EURCAD: 1.4700,
  EURCHF: 0.9600, GBPAUD: 1.9300, GBPCAD: 1.7150, GBPCHF: 1.1200, AUDNZD: 1.0850,
  EURNZD: 1.7950, NZDJPY: 90.45, CADCHF: 0.6530, AUDCAD: 0.8880, GBPNZD: 2.0950,
  USDNOK: 10.850, USDSEK: 10.350, USDMXN: 17.250, USDZAR: 18.650,
  // Commodities
  XAUUSD: 2345.80, XTIUSD: 78.50,
  // Indices
  SPX: 5120.50, NDX: 18250.0, DAX: 18050.0, UKX: 7950.0, N225: 38500.0,
  // Crypto
  BTCUSD: 64250.0, ETHUSD: 3450.00, BNBUSD: 585.00, SOLUSD: 145.50, XRPUSD: 0.5250,
  ADAUSD: 0.4450, DOGEUSD: 0.0850, DOTUSD: 7.250, MATICUSD: 0.5650, LTCUSD: 78.50,
  AVAXUSD: 35.50, LINKUSD: 14.85, UNIUSD: 9.850, ATOMUSD: 9.250, XLMUSD: 0.0950,
  ETCUSD: 28.50, NEARUSD: 5.850, APTUSD: 9.450, FILUSD: 4.950, ARBUSD: 1.150,
  OPUSD: 2.450, SANDUSD: 0.3850, MANAUSD: 0.3150, AAVEUSD: 85.50, GRTUSD: 0.2850,
  ALGOUSD: 0.1450, VETUSD: 0.0225, ICPUSD: 9.850, HBARUSD: 0.0750, FTMUSD: 0.2450,
};

export default function Dashboard({ activeSector, onSectorChange, currentSectorInfo }: DashboardProps) {
  const [prices, setPrices] = useState<Record<string, { price: number; change: number }>>({});
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    // Generate mock prices for current sector
    const newPrices: Record<string, { price: number; change: number }> = {};
    currentSectorInfo.instruments.forEach(symbol => {
      const basePrice = MOCK_PRICES[symbol] || 100;
      newPrices[symbol] = generateMockPrice(basePrice);
    });
    setPrices(newPrices);
    setLastUpdate(new Date().toLocaleTimeString());
  }, [activeSector, currentSectorInfo]);

  return (
    <div>
      <header className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">
          Market overview • Last updated: {lastUpdate}
        </p>
      </header>

      {/* Sector Selector */}
      <SectorSelector activeSector={activeSector} onSectorChange={onSectorChange} />

      {/* Stats Grid */}
      <div className="dashboard-grid">
        <div className="stat-card">
          <div className="stat-label">Active Instruments</div>
          <div className="stat-value">{currentSectorInfo.instruments.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Portfolio P&L</div>
          <div className="stat-value green">+$1,245.50</div>
          <div className="stat-change positive">+2.34% today</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Open Positions</div>
          <div className="stat-value">3</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Active Signals</div>
          <div className="stat-value" style={{ color: 'var(--accent-gold)' }}>5</div>
        </div>
      </div>

      {/* Instruments Section */}
      <section className="instruments-section">
        <h2 className="section-title">
          {currentSectorInfo.icon} {currentSectorInfo.name} Instruments ({currentSectorInfo.instruments.length})
        </h2>
        <div className="instruments-grid">
          {currentSectorInfo.instruments.slice(0, 20).map(symbol => {
            const data = prices[symbol];
            if (!data) return null;
            
            return (
              <div key={symbol} className="instrument-card">
                <div>
                  <div className="instrument-symbol">{symbol}</div>
                  <div className="instrument-name">
                    {currentSectorInfo.id === 'crypto' ? 'Crypto' :
                     currentSectorInfo.id === 'forex' ? 'Forex' :
                     currentSectorInfo.id === 'commodities' ? 'Commodity' :
                     currentSectorInfo.id === 'indices' ? 'Index' : 'Stock'}
                  </div>
                </div>
                <div className="instrument-price">
                  <div className="instrument-value">
                    {currentSectorInfo.id === 'crypto' || currentSectorInfo.id === 'commodities' 
                      ? `$${data.price.toLocaleString()}`
                      : data.price.toFixed(4)}
                  </div>
                  <div className={`instrument-change ${data.change >= 0 ? 'positive' : 'negative'}`}>
                    {data.change >= 0 ? '+' : ''}{data.change.toFixed(2)}%
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        {currentSectorInfo.instruments.length > 20 && (
          <p style={{ marginTop: '12px', color: 'var(--text-secondary)', fontSize: '14px' }}>
            +{currentSectorInfo.instruments.length - 20} more instruments
          </p>
        )}
      </section>
    </div>
  );
}