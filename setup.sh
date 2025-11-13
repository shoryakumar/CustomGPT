#!/bin/bash
# Quick setup script for Custom GPT Demo

echo "🚀 Setting up Biorhyme Health Custom GPT Demo..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Check if .env file exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "The .env file should already be present with RDS credentials."
    echo "If missing, please create it from .env.example"
    exit 1
else
    echo "✓ .env file found"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo ""
echo "🗄️  Setting up PostgreSQL database..."
echo "Connecting to RDS..."
python3 manage.py migrate

# Load demo data
echo ""
echo "📊 Loading demo data..."
python3 manage.py load_demo_data

# Success message
echo ""
echo "✅ Setup complete!"
echo ""
echo "📦 Database: PostgreSQL (AWS RDS)"
echo "🔗 Host: ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com"
echo ""
echo "To start the server, run:"
echo "  python3 manage.py runserver"
echo ""
echo "Then visit: http://localhost:8000"
echo ""
echo "Try the chatbot:"
echo '  curl -X POST http://localhost:8000/api/chat/ -H "Content-Type: application/json" -d '"'"'{"message": "What did I eat today?"}'"'"''
echo ""
