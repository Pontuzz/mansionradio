#!/bin/bash
# MansionRadio Bot - Bare Metal Installation Script
# 
# Automates the complete installation of MansionRadio Bot on a Linux system.
# Works on: Ubuntu 20.04+, Debian 11+, Raspberry Pi OS
#
# Usage:
#   bash install.sh                    # Interactive installation
#   bash install.sh --help             # Show help
#   bash install.sh --user radiobot    # Specify custom user
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BOT_USER="radiobot"
BOT_HOME="/home/${BOT_USER}"
BOT_DIR="${BOT_HOME}/mansion-radio-bot"
PYTHON_CMD="python3"
SKIP_SYSTEMD=false
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --user)
            BOT_USER="$2"
            BOT_HOME="/home/${BOT_USER}"
            BOT_DIR="${BOT_HOME}/mansion-radio-bot"
            shift 2
            ;;
        --no-systemd)
            SKIP_SYSTEMD=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            cat << EOF
MansionRadio Bot - Bare Metal Installation

Usage: bash install.sh [OPTIONS]

Options:
  --user USERNAME          Create/use dedicated user (default: radiobot)
  --no-systemd             Skip systemd service setup (manual only)
  --dry-run                Show what would be done without making changes
  --help, -h               Show this help message

Examples:
  bash install.sh
  bash install.sh --user botuser
  bash install.sh --no-systemd
  bash install.sh --dry-run

EOF
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper function for dry-run
run_or_echo() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] $@"
    else
        eval "$@"
    fi
}

# Helper function for sudo
sudo_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] sudo $@"
    else
        sudo "$@"
    fi
}

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     MansionRadio Bot - Installation         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${BLUE}[1/7]${NC} Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Install with: sudo apt install python3.11 python3.11-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓${NC} Found Python $PYTHON_VERSION"

if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}✗ pip3 is not installed${NC}"
    echo "Install with: sudo apt install python3-pip"
    exit 1
fi

echo -e "${GREEN}✓${NC} pip3 is available"

if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} git is not installed (optional for updates)"
fi

echo ""

# Step 2: Create user
echo -e "${BLUE}[2/7]${NC} Setting up user account..."

if id "$BOT_USER" &>/dev/null; then
    echo -e "${YELLOW}⚠${NC} User $BOT_USER already exists"
else
    echo "Creating user $BOT_USER..."
    sudo_cmd useradd -m -s /bin/bash -d "$BOT_HOME" "$BOT_USER"
    echo -e "${GREEN}✓${NC} User $BOT_USER created"
fi

echo ""

# Step 3: Copy project files
echo -e "${BLUE}[3/7]${NC} Installing bot files..."

if [ ! -d "$BOT_DIR" ]; then
    run_or_echo mkdir -p "$BOT_DIR"
    echo -e "${GREEN}✓${NC} Created directory $BOT_DIR"
fi

# Copy files from current directory to bot directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
echo "Copying files from $SCRIPT_DIR..."

for item in src config docker scripts systemd requirements.txt README.md; do
    if [ -e "$SCRIPT_DIR/$item" ]; then
        run_or_echo cp -r "$SCRIPT_DIR/$item" "$BOT_DIR/"
        echo -e "${GREEN}✓${NC} Copied $item"
    fi
done

# Fix ownership
sudo_cmd chown -R "$BOT_USER:$BOT_USER" "$BOT_DIR"
echo -e "${GREEN}✓${NC} Set ownership to $BOT_USER:$BOT_USER"

echo ""

# Step 4: Create virtual environment
echo -e "${BLUE}[4/7]${NC} Creating Python virtual environment..."

run_or_echo "cd $BOT_DIR && python3 -m venv venv"
echo -e "${GREEN}✓${NC} Virtual environment created"

echo ""

# Step 5: Install dependencies
echo -e "${BLUE}[5/7]${NC} Installing Python dependencies..."

run_or_echo "cd $BOT_DIR && source venv/bin/activate && pip install --upgrade pip"
run_or_echo "cd $BOT_DIR && source venv/bin/activate && pip install -r requirements.txt"
echo -e "${GREEN}✓${NC} Dependencies installed"

echo ""

# Step 6: Configure environment
echo -e "${BLUE}[6/7]${NC} Setting up configuration..."

if [ ! -f "$BOT_DIR/.env" ]; then
    run_or_echo "cp $BOT_DIR/config/.env.example $BOT_DIR/.env"
    sudo_cmd chown "$BOT_USER:$BOT_USER" "$BOT_DIR/.env"
    sudo_cmd chmod 600 "$BOT_DIR/.env"
    echo -e "${GREEN}✓${NC} Created .env file (needs configuration)"
    echo -e "${YELLOW}⚠${NC}  Edit $BOT_DIR/.env with your IRC settings"
else
    echo -e "${YELLOW}⚠${NC} .env file already exists"
fi

echo ""

# Step 7: Setup systemd service
echo -e "${BLUE}[7/7]${NC} Setting up systemd service..."

if [ "$SKIP_SYSTEMD" = false ]; then
    SERVICE_FILE="/etc/systemd/system/mansion-radio-bot.service"
    
    # Create service file with correct paths
    SERVICE_CONTENT="[Unit]
Description=MansionNET Radio IRC Bot
Documentation=file://${BOT_DIR}/README.md
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${BOT_USER}
Group=${BOT_USER}
WorkingDirectory=${BOT_DIR}
Environment=\"PATH=${BOT_DIR}/venv/bin\"
ExecStart=${BOT_DIR}/venv/bin/python src/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mansion-radio-bot

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${BOT_DIR}

[Install]
WantedBy=multi-user.target
"
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] Would create $SERVICE_FILE"
        echo "$SERVICE_CONTENT"
    else
        echo "$SERVICE_CONTENT" | sudo_cmd tee "$SERVICE_FILE" > /dev/null
        sudo_cmd systemctl daemon-reload
        echo -e "${GREEN}✓${NC} Systemd service installed"
    fi
    
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Edit configuration:"
    echo "     sudo nano $BOT_DIR/.env"
    echo ""
    echo "  2. Test the bot:"
    echo "     sudo -u $BOT_USER bash -c 'cd $BOT_DIR && source venv/bin/activate && python src/main.py'"
    echo ""
    echo "  3. Enable and start service:"
    echo "     sudo systemctl enable mansion-radio-bot"
    echo "     sudo systemctl start mansion-radio-bot"
    echo ""
    echo "  4. Check status:"
    echo "     sudo systemctl status mansion-radio-bot"
    echo "     sudo journalctl -u mansion-radio-bot -f"
else
    echo -e "${YELLOW}⚠${NC}  Systemd setup skipped (--no-systemd)"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Edit configuration:"
    echo "     nano $BOT_DIR/.env"
    echo ""
    echo "  2. Run the bot manually:"
    echo "     cd $BOT_DIR && source venv/bin/activate && python src/main.py"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Installation Complete!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo "Installation directory: $BOT_DIR"
echo "Bot user: $BOT_USER"
echo "Configuration: $BOT_DIR/.env"
echo ""
