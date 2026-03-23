#!/bin/bash
# AgentFinance v3 - Full Installation Script for Kali Linux
# Author: AgentFinance Team
# Last Updated: 2026-03-20

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          AgentFinance v3 - Full Installation                  ║"
echo "║          Intelligence + Trading Automation                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_warning "Running as root - some commands may not need sudo"
fi

# Detect OS
if ! command -v lsb_release &> /dev/null; then
    log_info "Installing lsb-release..."
    sudo apt-get update && sudo apt-get install -y lsb-release
fi

OS=$(lsb_release -is 2>/dev/null || echo "Linux")
DIST=$(lsb_release -cs 2>/dev/null || echo "unknown")

log_info "Detected OS: $OS ($DIST)"

# ============================================================================
# 1. CORE SYSTEM DEPENDENCIES
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Installing Core System Dependencies"
echo "═══════════════════════════════════════════════════════════════════"

sudo apt-get update
sudo apt-get install -y \
    git curl wget \
    build-essential \
    python3 python3-pip python3-venv \
    python3-dev \
    golang-go \
    redis-server \
    postgresql-client \
    jq \
    htop \
    tmux \
    screen

log_success "Core dependencies installed"

# ============================================================================
# 2. PYTHON ENVIRONMENT
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Setting Up Python Virtual Environment"
echo "═══════════════════════════════════════════════════════════════════"

# Create project directory
mkdir -p ~/agentfinance
cd ~/agentfinance

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

log_info "Virtual environment created"

# Upgrade pip
pip install --upgrade pip setuptools wheel

# ============================================================================
# 3. PYTHON PACKAGES
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Installing Python Packages"
echo "═══════════════════════════════════════════════════════════════════"

# Core data science
pip install \
    numpy \
    pandas \
    scipy \
    statsmodels

# Financial data
pip install \
    requests \
    aiohttp \
    websockets \
    python-dotenv

# Technical analysis
pip install \
    ta \
    ta-lib 2>/dev/null || log_warning "TA-Lib installation skipped (may require manual build)"

# Optional: VectorBT for backtesting
pip install vectorbt || log_warning "VectorBT installation skipped"

# Smart Money Concepts (if available)
pip install smartmoneyconcepts || log_warning "smartmoneyconcepts not available on PyPI"

# NLP (local sentiment)
pip install \
    transformers \
    torch \
    sentencepiece

# cTrader OpenAPI (TCP/Protobuf trading client)
pip install twisted protobuf ctrader-open-api==0.9.2 || \
    log_warning "ctrader-open-api installation skipped"

# Install MCP server for AI trading agents
pip install mcp>=0.9.0 || log_warning "MCP server installation skipped"

log_success "Python packages installed"

# ============================================================================
# 4. NODE.JS & NPM
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Installing Node.js & npm"
echo "═══════════════════════════════════════════════════════════════════"

if ! command -v node &> /dev/null; then
    # Install Node.js via nodesource
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
    sudo apt-get install -y nodejs
    
    log_success "Node.js installed"
else
    log_info "Node.js already installed: $(node --version)"
fi

# ============================================================================
# 5. TRADER CLI
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Installing Trading CLI Tools"
echo "═══════════════════════════════════════════════════════════════════"

# cTrader CLI (if available)
npm install -g @spotware/ctrader-cli 2>/dev/null || log_warning "cTrader CLI skipped"

# Paperclip CLI
# npm install -g @paperclip/cli 2>/dev/null || log_warning "Paperclip CLI skipped"

log_success "Trading CLI tools installed"

# ============================================================================
# 6. GO INDICATOR LIBRARY (Optional)
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Installing Go Indicator Library"
echo "═══════════════════════════════════════════════════════════════════"

if [ -d ~/agency ]; then
    mkdir -p ~/agency/indicator
    cd ~/agency/indicator
    
    if [ -d .git ]; then
        git pull
    else
        git clone https://github.com/cinar/indicator ~/agency/indicator 2>/dev/null || \
        log_warning "Could not clone indicator library"
    fi
    
    # Build indicator binary
    if [ -f "go.mod" ]; then
        go build -o ~/agency/bin/indicator ./cmd/indicator/ 2>/dev/null || \
        log_warning "Could not build indicator library"
    fi
    
    cd ~/agentfinance
    log_success "Go indicator library processed"
else
    log_info "Creating agency directory structure"
    mkdir -p ~/agency/{bin,scripts,skills,agents,trading}
fi

# ============================================================================
# 7. COPY AGENTFINANCE FILES
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Copying AgentFinance Files"
echo "═══════════════════════════════════════════════════════════════════"

# Copy trading engine
mkdir -p ~/agentfinance/trading/{engines,execution,backtest,strategies}
mkdir -p ~/agentfinance/agents
mkdir -p ~/agentfinance/n8n
mkdir -p ~/agentfinance/dashboard

log_success "Directory structure created"

# ============================================================================
# 8. ENVIRONMENT CONFIGURATION
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Creating Environment Configuration"
echo "═══════════════════════════════════════════════════════════════════"

cat > ~/agentfinance/.env.example << 'EOF'
# AgentFinance v3 Environment Configuration
# Copy to .env and fill in your credentials

# ============================================================================
# DATA PROVIDERS
# ============================================================================
POLYGON_API_KEY=your_polygon_key
OANDA_API_KEY=your_oanda_key
OANDA_ACCOUNT_ID=your_oanda_account
FRED_API_KEY=your_fred_key
NEWSAPI_KEY=your_newsapi_key

# ============================================================================
# CTRADER LIVE TRADING (Pepperstone Demo: Account ID 46729678)
# ============================================================================
# Get credentials from: https://help.ctrader.com/open-api/creating-new-app/
CTRADER_CLIENT_ID=your_ctrader_client_id
CTRADER_CLIENT_SECRET=your_ctrader_client_secret
CTRADER_ACCESS_TOKEN=your_ctrader_access_token
CTRADER_ACCOUNT_ID=46729678
CTRADER_HOST=demo          # "demo" for Pepperstone demo, "live" for real account

# ============================================================================
# TRADING PARAMETERS
# ============================================================================
MAX_RISK_PER_TRADE=0.01     # 1% risk per trade
MAX_DAILY_DRAWDOWN=0.03     # 3% daily halt threshold
INITIAL_BALANCE=10000       # Starting balance

# ============================================================================
# NOTIFICATIONS
# ============================================================================
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
EOF

if [ ! -f ~/agentfinance/.env ]; then
    cp ~/agentfinance/.env.example ~/agentfinance/.env
    log_warning "Created .env file - please update with your API keys"
fi

# ============================================================================
# 9. REDIS SETUP
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Setting Up Redis"
echo "═══════════════════════════════════════════════════════════════════"

sudo systemctl enable redis-server 2>/dev/null || true
sudo systemctl start redis-server 2>/dev/null || true

if systemctl is-active --quiet redis-server; then
    log_success "Redis is running"
else
    log_warning "Redis could not be started - some caching features may not work"
fi

# ============================================================================
# 10. VERIFICATION
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Verification"
echo "═══════════════════════════════════════════════════════════════════"

# Check Python packages
log_info "Checking Python packages..."
source ~/agentfinance/venv/bin/activate
python3 -c "import pandas; print('  ✓ pandas', pandas.__version__)"
python3 -c "import numpy; print('  ✓ numpy', numpy.__version__)"
python3 -c "import requests; print('  ✓ requests', requests.__version__)"

# Check cTrader packages
python3 -c "import twisted; print('  ✓ twisted', twisted.__version__)" 2>/dev/null || log_warning "  twisted not installed"
python3 -c "import ctrader_open_api; print('  ✓ ctrader-open-api installed')" 2>/dev/null || log_warning "  ctrader-open-api not installed"

# Verify cTrader client can be imported
python3 -c "import sys; sys.path.insert(0,'../trading/execution'); from ctrader_client import CTraderClient; print('  ✓ CTraderClient ready')" 2>/dev/null || log_warning "  ctrader_client import failed"

# Check Docker
if command -v docker &> /dev/null; then
    log_info "Docker: $(docker --version | cut -d' ' -f3 | cut -d',' -f1)"
    if docker ps &> /dev/null; then
        log_success "Docker daemon is running"
    else
        log_warning "Docker is installed but daemon is not running"
    fi
else
    log_warning "Docker not found — cTrader REST API Docker option skipped"
fi

# Check Node.js
if command -v node &> /dev/null; then
    log_info "Node.js: $(node --version)"
fi

# Check Go
if command -v go &> /dev/null; then
    log_info "Go: $(go version | cut -d' ' -f3)"
fi

# ============================================================================
# COMPLETION
# ============================================================================
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║              AgentFinance v3 Installation Complete!            ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next Steps:"
echo "  1. Activate the virtual environment:"
echo "     source ~/agentfinance/venv/bin/activate"
echo ""
echo "  2. Update your API keys in:"
echo "     nano ~/agentfinance/.env"
echo "     (cTrader: CTRADER_CLIENT_ID, CTRADER_CLIENT_SECRET, CTRADER_ACCESS_TOKEN)"
echo ""
echo "  3. OPTIONAL — Deploy cTrader REST API via Docker:"
echo "     cd ~/agentfinance/ctrader"
echo "     cp .env.example ../.env  # Add your credentials"
echo "     docker compose up --build -d"
echo "     curl http://localhost:9009/health"
echo "     # Swagger UI: http://localhost:9009/docs"
echo ""
echo "  4. Test cTrader connection (direct or via Docker REST):"
echo "     cd ~/agentfinance && source venv/bin/activate"
echo "     # Direct TCP (no Docker):"
echo "     python3 trading/execution/ctrader_client.py"
echo "     # Via Docker REST:"
echo "     python3 -c \"from ctrader.rest_client import CTraderRESTClient; c=CTraderRESTClient(); c.connect(); print(c.get_positions())\""
echo ""
echo "  5. Test Agent 28 (Live Executor):"
echo "     python3 agents/trading/live_executor.py positions"
echo ""
echo "  6. Run the SMC Pipeline:"
echo "     python3 trading/execution/smc_pipeline.py --scan-all --dry"
echo ""
echo "  7. Use the Unified Trading CLI:"
echo "     python3 scripts/agent_cli.py health        # Check system status"
echo "     python3 scripts/agent_cli.py scan EURUSD H1 --dry"
echo "     python3 scripts/agent_cli.py status"
echo "     python3 scripts/agent_cli.py risk"
echo "     python3 scripts/agent_cli.py session"
echo "     python3 scripts/agent_cli.py report --today"
echo ""
echo "  8. Automate with Daily Routine:"
echo "     python3 scripts/daily_routine.py --status    # Check routine status"
echo "     python3 scripts/daily_routine.py --run-all   # Run all phases (testing)"
echo "     python3 scripts/daily_routine.py --schedule  # Run automated schedule"
echo ""
echo "  9. Set up PostgreSQL Database:"
echo "     python3 database/setup_database.py --docker-compose  # Generate Docker Compose"
echo "     python3 database/setup_database.py --init            # Initialize schema"
echo "     python3 database/setup_database.py --status          # Check connection"
echo ""
echo "  10. Deploy Paperclip agents:"
echo "     cd ~/agentfinance && cp agents/*.yaml ~/agency/paperclip/agents/"
echo ""
echo "  11. Import n8n workflows:"
echo "     Open n8n UI at http://localhost:5678 and import workflows/n8n/*.json"
echo ""
echo "  12. Start the React dashboard:"
echo "     cd dashboard && npm run dev"
echo ""
echo "  13. Start the Trading Watchdog (dead man's switch):"
echo "     python3 trading/watchdog.py --status          # Check watchdog status"
echo "     python3 trading/watchdog.py --check           # Run single health check"
echo "     python3 trading/watchdog.py --heartbeat test  # Send test heartbeat"
echo "     # For production, run as systemd service:"
echo "     sudo cp scripts/agentfinance-watchdog.service /etc/systemd/system/"
echo "     sudo systemctl enable agentfinance-watchdog"
echo "     sudo systemctl start agentfinance-watchdog"
echo ""
echo "  14. Enable Redis caching (optional but recommended):"
echo "     redis-cli ping                            # Should return PONG"
echo "     # The MarketDataCache auto-detects Redis and falls back to filesystem"
echo "     # To force filesystem-only mode:"
echo "     #   REDIS_HOST='' python3 scripts/agent_cli.py scan EURUSD"
echo "     cd dashboard-app && npm run dev"
echo ""
echo "AgentFinance v3 is ready with:"
echo "  • 28 specialized agents"
echo "  • SMC Strategy Engine"
echo "  • 80+ Technical Indicators"
echo "  • cTrader Live Execution (Direct TCP or Docker REST API)"
echo "  • Full Risk Management"
echo "  • Unified Trading CLI (agent_cli.py)"
echo "  • Daily Routine Automation (daily_routine.py)"
echo "  • PostgreSQL Database Schema (setup_database.py)"
echo ""
