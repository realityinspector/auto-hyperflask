#!/bin/bash
set -e

echo "🚀 AutoHyperFlask - Automated Replit Setup"
echo "=========================================="
echo ""

# Check if already initialized
if [ -f .replit-initialized ]; then
    echo "✅ Already initialized, skipping setup..."
    echo "   To re-run setup, delete .replit-initialized and restart"
    exit 0
fi

echo "📦 Step 1/7: Setting up Python virtual environment..."
python3 -m venv venv --system-site-packages
source venv/bin/activate

echo "📦 Step 2/7: Upgrading pip..."
pip install --upgrade pip

echo "📦 Step 3/7: Installing Python dependencies..."
pip install -e ".[dev,e2e]"

echo "📦 Step 4/7: Installing Node.js dependencies..."
npm install

echo "🏗️  Step 5/7: Building frontend assets..."
npm run build

echo "🗄️  Step 6/7: Setting up database..."
cp config_dev.yml config.yml
python3 scripts/reset_db.py --seed --confirm

echo "🧪 Step 7/7: Running validation tests..."
python3 -m pytest tests/test_setup.py -v

# Mark as initialized
touch .replit-initialized

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎉 AutoHyperFlask is ready to use!"
echo ""
echo "📝 What's been configured:"
echo "   • Python virtual environment created"
echo "   • All dependencies installed"
echo "   • Frontend assets built (JS, CSS, icons)"
echo "   • Database initialized with test data"
echo "   • 8 validation tests passed"
echo ""
echo "🔑 Test accounts (password: 'password'):"
echo "   • user1@test.com"
echo "   • user2@test.com"
echo "   • admin@test.com"
echo ""
echo "🌐 Access your app:"
echo "   • Local: http://localhost:5000"
echo "   • Replit: Check the webview panel"
echo ""
echo "📚 Next steps:"
echo "   • Click 'Run' to start the development server"
echo "   • Visit /timeline to see seeded data"
echo "   • Visit /admin for admin dashboard"
echo ""
