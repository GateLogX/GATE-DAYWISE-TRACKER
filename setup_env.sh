#!/bin/bash

# Interactive Environment Setup Script
# This script will help you configure your .env file

echo "🔧 GATE Voice Assistant - Environment Setup"
echo "==========================================="
echo ""

ENV_FILE="backend/.env"

# Check if .env already exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating .env file from template..."
    cp backend/.env.example "$ENV_FILE"
fi

echo "I'll help you set up the required credentials."
echo "Don't worry, you can skip any step and add them later!"
echo ""

# Function to update env variable
update_env() {
    local key=$1
    local prompt=$2
    local default=$3
    local is_secret=${4:-false}
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$prompt"
    
    if [ -n "$default" ]; then
        echo "Current value: $default"
    fi
    
    if [ "$is_secret" = true ]; then
        read -p "Enter new value (or press Enter to skip): " -s value
        echo ""
    else
        read -p "Enter new value (or press Enter to skip): " value
    fi
    
    if [ -n "$value" ]; then
        # Use sed to update the value in .env file
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
        else
            # Linux
            sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
        fi
        echo "✅ Updated $key"
    else
        echo "⏭️  Skipped $key"
    fi
    echo ""
}

echo "📱 STEP 1: Twilio WhatsApp Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To get Twilio credentials:"
echo "1. Go to https://www.twilio.com/try-twilio"
echo "2. Sign up for a free account"
echo "3. Go to Console Dashboard"
echo "4. Find your Account SID and Auth Token"
echo ""
read -p "Press Enter when you're ready (or Ctrl+C to exit)..."
echo ""

update_env "TWILIO_ACCOUNT_SID" "📝 Enter your Twilio Account SID:" "your_twilio_account_sid_here" true
update_env "TWILIO_AUTH_TOKEN" "🔐 Enter your Twilio Auth Token:" "your_twilio_auth_token_here" true

echo "📞 STEP 2: WhatsApp Number"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your WhatsApp number should be in format: whatsapp:+919876543210"
echo "Make sure to include country code (91 for India)"
echo ""

update_env "YOUR_WHATSAPP_NUMBER" "📱 Enter your WhatsApp number:" "whatsapp:+919876543210" false

echo "🤖 STEP 3: OpenAI API Key"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To get OpenAI API key:"
echo "1. Go to https://platform.openai.com/signup"
echo "2. Create an account"
echo "3. Go to https://platform.openai.com/api-keys"
echo "4. Create a new API key"
echo ""
echo "⚠️  Note: You'll need to add payment method ($5-10 should be enough)"
echo ""
read -p "Press Enter when you're ready (or Ctrl+C to exit)..."
echo ""

update_env "OPENAI_API_KEY" "🔑 Enter your OpenAI API Key:" "your_openai_api_key_here" true

echo "⏰ STEP 4: Schedule Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "What time should you receive daily check-in messages?"
echo "Format: HH:MM (24-hour format)"
echo ""

update_env "DAILY_CHECKIN_TIME" "🕐 Enter time (e.g., 20:00 for 8 PM):" "20:00" false

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Configuration Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show current configuration (hiding secrets)
echo "📋 Your Current Configuration:"
echo ""
echo "Twilio Account SID: $(grep '^TWILIO_ACCOUNT_SID=' "$ENV_FILE" | cut -d= -f2 | sed 's/\(.\{4\}\).*/\1***/')"
echo "Twilio Auth Token: $(grep '^TWILIO_AUTH_TOKEN=' "$ENV_FILE" | cut -d= -f2 | sed 's/\(.\{4\}\).*/\1***/')"
echo "WhatsApp Number: $(grep '^YOUR_WHATSAPP_NUMBER=' "$ENV_FILE" | cut -d= -f2)"
echo "OpenAI API Key: $(grep '^OPENAI_API_KEY=' "$ENV_FILE" | cut -d= -f2 | sed 's/\(.\{7\}\).*/\1***/')"
echo "Daily Check-in Time: $(grep '^DAILY_CHECKIN_TIME=' "$ENV_FILE" | cut -d= -f2)"
echo "Timezone: $(grep '^TIMEZONE=' "$ENV_FILE" | cut -d= -f2)"
echo ""

# Check what still needs to be configured
needs_config=false
if grep -q "your_twilio_account_sid_here" "$ENV_FILE"; then
    echo "⚠️  Twilio Account SID still needs to be configured"
    needs_config=true
fi
if grep -q "your_twilio_auth_token_here" "$ENV_FILE"; then
    echo "⚠️  Twilio Auth Token still needs to be configured"
    needs_config=true
fi
if grep -q "your_openai_api_key_here" "$ENV_FILE"; then
    echo "⚠️  OpenAI API Key still needs to be configured"
    needs_config=true
fi

echo ""
if [ "$needs_config" = false ]; then
    echo "🎉 All required credentials are configured!"
    echo ""
    echo "🚀 Next Steps:"
    echo "1. For WhatsApp to work locally, install ngrok:"
    echo "   Download from: https://ngrok.com/download"
    echo "   Run: ngrok http 5000"
    echo ""
    echo "2. Join Twilio WhatsApp Sandbox:"
    echo "   Go to: https://www.twilio.com/console/sms/whatsapp/sandbox"
    echo "   Send the code from your WhatsApp"
    echo ""
    echo "3. Start the server:"
    echo "   cd backend && python app.py"
    echo ""
    echo "4. Open dashboard:"
    echo "   Open dashboard.html in your browser"
else
    echo "⚠️  Some credentials are missing. You can:"
    echo "1. Run this script again: ./setup_env.sh"
    echo "2. Edit manually: nano backend/.env"
    echo ""
    echo "💡 The system will work without WhatsApp/Voice features"
    echo "   if you just want to test the timetable generation!"
fi

echo ""
echo "📚 For detailed instructions, see: SETUP_GUIDE.md"
echo ""
