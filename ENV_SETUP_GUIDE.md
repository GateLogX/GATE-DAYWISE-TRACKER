# 🔧 Environment Variables Setup - Simple Guide

## Quick Setup (Interactive)

Just run this command and follow the prompts:

```bash
cd /home/anu332002/GATE-DAYWISE-TRACKER
./setup_env.sh
```

The script will guide you through adding each credential!

---

## Manual Setup (Edit Directly)

If you prefer to edit manually:

```bash
cd /home/anu332002/GATE-DAYWISE-TRACKER
nano backend/.env
```

Or use any text editor you like!

---

## 📋 Required Credentials

### 1. **Twilio (for WhatsApp)** 📱

**Where to get:**
1. Go to: https://www.twilio.com/try-twilio
2. Sign up for FREE account
3. Go to Console Dashboard: https://console.twilio.com
4. Copy your **Account SID** and **Auth Token**

**Add to .env:**
```env
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcd
TWILIO_AUTH_TOKEN=your_32_character_auth_token_here
```

**Your WhatsApp Number:**
```env
YOUR_WHATSAPP_NUMBER=whatsapp:+919876543210
```
(Replace with your actual number including country code)

---

### 2. **OpenAI (for Voice Recognition)** 🎤

**Where to get:**
1. Go to: https://platform.openai.com/signup
2. Create account
3. Go to: https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

**Add to .env:**
```env
OPENAI_API_KEY=sk-proj-abc123xyz789...
```

**Cost:** ~$5-10 should be enough for the entire GATE preparation!

---

### 3. **Your Preferences** ⏰

**Daily Check-in Time:**
```env
DAILY_CHECKIN_TIME=20:00
```
(Change to your preferred time in 24-hour format)

**Timezone:**
```env
TIMEZONE=Asia/Kolkata
```
(Usually you don't need to change this)

---

## 🎯 What Each Variable Does

| Variable | Purpose | Required? |
|----------|---------|-----------|
| `TWILIO_ACCOUNT_SID` | Twilio account identifier | Only for WhatsApp |
| `TWILIO_AUTH_TOKEN` | Twilio authentication | Only for WhatsApp |
| `TWILIO_WHATSAPP_NUMBER` | Twilio's WhatsApp number | Only for WhatsApp |
| `YOUR_WHATSAPP_NUMBER` | Your WhatsApp number | Only for WhatsApp |
| `OPENAI_API_KEY` | For voice transcription | Only for voice |
| `DAILY_CHECKIN_TIME` | When to send messages | Yes |
| `TIMEZONE` | Your timezone | Yes |
| `FLASK_PORT` | Server port | No (default: 5000) |
| `BASE_URL` | For webhooks (ngrok) | Only for WhatsApp |

---

## 💡 Can I Skip Some?

**YES!** You can use the system without WhatsApp or Voice features:

### Option 1: Basic Mode (No WhatsApp)
- Skip Twilio and OpenAI credentials
- Use the web dashboard to:
  - Upload lectures
  - Set goals
  - View timetable
  - Manually update progress

### Option 2: WhatsApp Only (No Voice)
- Add Twilio credentials
- Skip OpenAI
- Reply with TEXT messages instead of voice

### Option 3: Full Features
- Add both Twilio and OpenAI
- Get voice recognition + WhatsApp

---

## 🚀 Quick Start Commands

### 1. Run Interactive Setup
```bash
cd /home/anu332002/GATE-DAYWISE-TRACKER
./setup_env.sh
```

### 2. View Current Configuration
```bash
cat backend/.env
```

### 3. Edit Manually
```bash
nano backend/.env
```
(Press `Ctrl+X`, then `Y`, then `Enter` to save)

### 4. Test Configuration
```bash
source venv/bin/activate
cd backend
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✅ Config loaded!')"
```

---

## 📱 Setting Up Twilio WhatsApp (Detailed)

### Step 1: Create Twilio Account
1. Go to: https://www.twilio.com/try-twilio
2. Sign up (it's FREE!)
3. Verify your email and phone

### Step 2: Get Credentials
1. Go to Console: https://console.twilio.com
2. You'll see **Account SID** and **Auth Token**
3. Click "Show" to reveal Auth Token
4. Copy both to your `.env` file

### Step 3: Join WhatsApp Sandbox
1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. You'll see a code like: "join <random-words>"
3. Send this message from your WhatsApp to: +1 415 523 8886
4. You'll receive confirmation

### Step 4: Set Webhook (for local testing)
1. Install ngrok: https://ngrok.com/download
2. Run: `ngrok http 5000`
3. Copy the URL (e.g., `https://abc123.ngrok.io`)
4. Go to Twilio Console → WhatsApp → Sandbox Settings
5. Set "When a message comes in" to: `https://abc123.ngrok.io/webhook/whatsapp`
6. Save

---

## 🤖 Setting Up OpenAI (Detailed)

### Step 1: Create Account
1. Go to: https://platform.openai.com/signup
2. Sign up with email
3. Verify your email

### Step 2: Add Payment Method
1. Go to: https://platform.openai.com/account/billing
2. Add credit card
3. Add $5-10 credit (this will last months!)

### Step 3: Create API Key
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Give it a name like "GATE Voice Assistant"
4. Copy the key (starts with `sk-`)
5. **Save it immediately** - you won't see it again!

### Step 4: Add to .env
```env
OPENAI_API_KEY=sk-proj-your_actual_key_here
```

---

## 🔒 Security Tips

1. **Never share** your `.env` file
2. **Never commit** `.env` to Git (it's already in .gitignore)
3. **Regenerate keys** if accidentally exposed
4. **Use sandbox** for testing WhatsApp

---

## ❌ Troubleshooting

### "Module 'dotenv' not found"
```bash
source venv/bin/activate
pip install python-dotenv
```

### "Invalid Twilio credentials"
- Check Account SID starts with "AC"
- Check Auth Token is 32 characters
- Make sure no extra spaces

### "OpenAI API error"
- Check key starts with "sk-"
- Verify billing is set up
- Check you have credit

### "WhatsApp not working"
- Did you join the sandbox?
- Is ngrok running?
- Is webhook URL set correctly?
- Check phone number format: `whatsapp:+919876543210`

---

## 📝 Example .env File

Here's what a configured `.env` looks like:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcd
TWILIO_AUTH_TOKEN=your32characterauthtokenhere123
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
YOUR_WHATSAPP_NUMBER=whatsapp:+919876543210

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-abc123xyz789defghij...

# Schedule
DAILY_CHECKIN_TIME=20:00
TIMEZONE=Asia/Kolkata

# Flask
FLASK_PORT=5000
FLASK_DEBUG=True

# Webhook (add after starting ngrok)
BASE_URL=https://abc123xyz.ngrok.io
```

---

## 🎉 After Configuration

Once you've added the credentials:

```bash
# 1. Start the server
cd backend
python app.py

# 2. Open dashboard
# Open dashboard.html in your browser

# 3. Upload your Excel file
# Use the dashboard UI

# 4. Set your goals
# Use the dashboard UI

# 5. Start WhatsApp messages
# Click "Start Daily Messages" in dashboard
```

---

## 💰 Cost Breakdown

| Service | Free Tier | Cost |
|---------|-----------|------|
| Twilio Trial | $15.50 credit | FREE to start |
| Twilio Messages | 1¢ per message | ~$2.43 for 243 days |
| OpenAI Whisper | First $5 free | ~$5-10 total |
| **Total** | | **~$7-12 for entire GATE prep** |

**That's less than ₹1,000 for an AI assistant!** 🎯

---

## 🤔 Still Confused?

1. **Run the interactive setup:**
   ```bash
   ./setup_env.sh
   ```
   
2. **Or just start without WhatsApp:**
   - Use only the web dashboard
   - Manually track progress
   - Add WhatsApp later when ready

3. **Need help?**
   - Check SETUP_GUIDE.md for more details
   - Test with: `python test_system.py`

---

**You've got this! The system is ready once you add the credentials! 💪**
