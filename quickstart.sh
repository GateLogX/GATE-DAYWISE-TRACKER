#!/bin/bash

# GATE Voice Assistant - Quick Start Script
# This script helps you set up and run the system

echo "🚀 GATE 2027 Voice Assistant - Quick Start"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
cd backend
pip install -q -r requirements.txt
cd ..

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env from template..."
    cp backend/.env.example backend/.env
    echo ""
    echo "⚠️  IMPORTANT: Please edit backend/.env with your credentials:"
    echo "   - Twilio Account SID and Auth Token"
    echo "   - OpenAI API Key"
    echo "   - Your WhatsApp number"
    echo ""
    read -p "Press Enter after you've updated .env file..."
fi

# Convert CSV to Excel if needed
if [ ! -f "video_durations_detailed.xlsx" ]; then
    if [ -f "video_durations_detailed.csv" ]; then
        echo "📊 Converting CSV to Excel..."
        python3 convert_csv_to_excel.py
    else
        echo "⚠️  No lecture data file found!"
        echo "   Please ensure video_durations_detailed.csv exists"
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Start the server: cd backend && python app.py"
echo "2. In another terminal, run: python test_system.py"
echo "3. Set up ngrok for WhatsApp webhooks (see SETUP_GUIDE.md)"
echo ""
echo "📚 Full guide: SETUP_GUIDE.md"
echo ""

# Ask if user wants to start server now
read -p "Start the Flask server now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting server..."
    cd backend
    python app.py
fi
