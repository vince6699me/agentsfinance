export type Sector = 'forex' | 'commodities' | 'stocks' | 'indices' | 'crypto';

export interface SectorInfo {
  id: Sector;
  name: string;
  icon: string;
  instruments: string[];
}

export const SECTORS: SectorInfo[] = [
  {
    id: 'forex',
    name: 'Forex',
    icon: '💱',
    instruments: [
      'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD',
      'USDCAD', 'NZDUSD', 'EURGBP', 'EURJPY', 'GBPJPY',
      'AUDJPY', 'CADJPY', 'CHFJPY', 'EURAUD', 'EURCAD',
      'EURCHF', 'GBPAUD', 'GBPCAD', 'GBPCHF', 'AUDNZD',
      'EURNZD', 'NZDJPY', 'CADCHF', 'AUDCAD', 'GBPNZD',
      'USDNOK', 'USDSEK', 'USDMXN', 'USDZAR'
    ]
  },
  {
    id: 'commodities',
    name: 'Commodities',
    icon: '⚡',
    instruments: ['XAUUSD', 'XTIUSD']
  },
  {
    id: 'stocks',
    name: 'Stocks',
    icon: '📈',
    instruments: [
      'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'BRK.B',
      'JPM', 'JNJ', 'V', 'UNH', 'PG', 'MA', 'HD', 'CVX',
      'MRK', 'ABBV', 'PEP', 'KO', 'COST', 'AVGO', 'LLY', 'WMT',
      'TMO', 'MCD', 'CSCO', 'ACN', 'ABT', 'DHR', 'NEE', 'TXN'
    ]
  },
  {
    id: 'indices',
    name: 'Indices',
    icon: '📊',
    instruments: ['SPX', 'NDX', 'DAX', 'UKX', 'N225']
  },
  {
    id: 'crypto',
    name: 'Crypto',
    icon: '₿',
    instruments: [
      'BTCUSD', 'ETHUSD', 'BNBUSD', 'SOLUSD', 'XRPUSD',
      'ADAUSD', 'DOGEUSD', 'DOTUSD', 'MATICUSD', 'LTCUSD',
      'AVAXUSD', 'LINKUSD', 'UNIUSD', 'ATOMUSD', 'XLMUSD',
      'ETCUSD', 'NEARUSD', 'APTUSD', 'FILUSD', 'ARBUSD',
      'OPUSD', 'SANDUSD', 'MANAUSD', 'AAVEUSD', 'GRTUSD',
      'ALGOUSD', 'VETUSD', 'ICPUSD', 'HBARUSD', 'FTMUSD'
    ]
  }
];

interface SectorSelectorProps {
  activeSector: Sector;
  onSectorChange: (sector: Sector) => void;
}

export default function SectorSelector({ activeSector, onSectorChange }: SectorSelectorProps) {
  return (
    <div className="sector-selector">
      <span className="sector-label">Select Market Sector</span>
      <div className="sector-buttons">
        {SECTORS.map((sector) => (
          <button
            key={sector.id}
            className={`sector-btn ${activeSector === sector.id ? 'active' : ''}`}
            onClick={() => onSectorChange(sector.id)}
          >
            <span className="sector-icon">{sector.icon}</span>
            {sector.name}
          </button>
        ))}
      </div>
    </div>
  );
}