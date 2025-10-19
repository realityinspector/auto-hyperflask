#!/bin/bash
set -e

# Ensure initialization has completed
if [ ! -f .replit-initialized ]; then
    echo "⚠️  Setup not complete. Running setup script..."
    bash scripts/replit-setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Set development environment
export FLASK_ENV=development
export FLASK_DEBUG=1

# Ensure we're using dev config
cp config_dev.yml config.yml

# Run development server
echo ""
echo "🚀 Starting AutoHyperFlask development server..."
echo "📝 Access your app at: http://localhost:5000"
echo ""
python3 -m hyperflask dev
