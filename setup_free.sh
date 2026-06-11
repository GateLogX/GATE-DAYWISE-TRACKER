#!/bin/bash

# FREE Version Setup - No API Keys Needed!
# This sets up the system to work without WhatsApp or Voice features

echo "🆓 GATE Voice Assistant - FREE Version Setup"
echo "=============================================="
echo ""
echo "This will set up the system WITHOUT WhatsApp or Voice features."
echo "You'll be able to:"
echo "  ✅ Upload your lecture data"
echo "  ✅ Generate smart timetables"
echo "  ✅ Track your progress manually"
echo "  ✅ View daily goals and schedules"
echo "  ✅ See completion statistics"
echo ""
echo "No credit card or API keys needed! 🎉"
echo ""
read -p "Press Enter to continue..."

ENV_FILE="backend/.env"

# Create .env from template if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    cp backend/.env.example "$ENV_FILE"
fi

# Update .env for free mode
echo "📝 Configuring for FREE mode..."

# Set dummy values that won't be used
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|^TWILIO_ACCOUNT_SID=.*|TWILIO_ACCOUNT_SID=not_configured|" "$ENV_FILE"
    sed -i '' "s|^TWILIO_AUTH_TOKEN=.*|TWILIO_AUTH_TOKEN=not_configured|" "$ENV_FILE"
    sed -i '' "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=not_configured|" "$ENV_FILE"
else
    # Linux
    sed -i "s|^TWILIO_ACCOUNT_SID=.*|TWILIO_ACCOUNT_SID=not_configured|" "$ENV_FILE"
    sed -i "s|^TWILIO_AUTH_TOKEN=.*|TWILIO_AUTH_TOKEN=not_configured|" "$ENV_FILE"
    sed -i "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=not_configured|" "$ENV_FILE"
fi

echo "✅ Configuration complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 How to Use the FREE Version"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Start the server:"
echo "    cd backend && python app.py"
echo ""
echo "2️⃣  Open the dashboard:"
echo "    Open dashboard.html in your browser"
echo "    Or go to: http://localhost:5000"
echo ""
echo "3️⃣  Upload your Excel file:"
echo "    File: video_durations_detailed.xlsx"
echo "    Click 'Upload & Parse' button"
echo ""
echo "4️⃣  Set your goals:"
echo "    - Target date: Feb 7, 2027 (GATE 2027)"
echo "    - Daily study hours: 6 hours"
echo "    - Practice time: 20%"
echo ""
echo "5️⃣  View your timetable:"
echo "    See today's schedule and weekly plan"
echo ""
echo "6️⃣  Update progress manually:"
echo "    Use the dashboard to mark lectures complete"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 Pro Tips"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Instead of WhatsApp:"
echo "   - Set a daily alarm on your phone for 8 PM"
echo "   - Open the dashboard and check today's goals"
echo "   - Manually mark completed lectures"
echo ""
echo "🎤 Instead of Voice:"
echo "   - Keep a simple checklist on paper"
echo "   - Or use the dashboard's manual input"
echo ""
echo "📊 Track Progress:"
echo "   - Dashboard shows real-time statistics"
echo "   - See completion percentage per subject"
echo "   - View your study streak"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 You're all set for FREE!"
echo ""
echo "Want to add WhatsApp/Voice later?"
echo "Run: ./setup_env.sh (you'll need API keys then)"
echo ""
