#!/bin/bash
set -e

echo "🚀 Deploying AutoHyperFlask to production..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Build production assets
echo "🏗️  Building production assets..."
npm run build

# Switch to production config
echo "⚙️  Switching to production configuration..."
cp config_prod.yml config.yml

# Create production database (if doesn't exist)
echo "🗄️  Initializing production database..."
python3 -c "
from hyperflask.factory import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Database initialized')
"

echo ""
echo "✅ Production setup complete!"
echo "🌐 Deploying to Cloud Run..."
echo ""

# Deploy
python3 -m hyperflask deploy
