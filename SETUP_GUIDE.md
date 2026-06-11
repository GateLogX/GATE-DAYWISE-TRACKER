# GATE 2027 Voice Assistant - Complete Setup Guide

## 🎯 What This System Does

This intelligent voice assistant helps you prepare for GATE 2027 by:

1. **📊 Smart Timetable Generation**: Automatically creates a personalized study schedule based on your Excel lecture list
2. **📱 WhatsApp Integration**: Sends daily progress check-ins via WhatsApp
3. **🎤 Voice Recognition**: Accepts voice replies about completed lectures
4. **🤖 Intelligent Adjustment**: Dynamically adjusts your timetable if you fall behind or get ahead
5. **📝 Practice Time Management**: Automatically allocates 20% time for practice sessions
6. **📈 Progress Tracking**: Tracks your completion rate and keeps you motivated

---

## 🚀 Quick Start Guide

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:

```env
# Get these from https://www.twilio.com/console
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
YOUR_WHATSAPP_NUMBER=whatsapp:+919876543210

# Get this from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Your preferred check-in time
DAILY_CHECKIN_TIME=20:00
TIMEZONE=Asia/Kolkata
```

### Step 3: Set Up Twilio WhatsApp Sandbox

1. Go to https://www.twilio.com/console/sms/whatsapp/sandbox
2. Send the join code from your WhatsApp to the Twilio number
3. You'll receive a confirmation message

### Step 4: Set Up Ngrok (for local development)

```bash
# Install ngrok
# Download from https://ngrok.com/download

# Run ngrok
ngrok http 5000
```

Copy the ngrok URL (e.g., `https://xxxx-xx-xx-xxx-xxx.ngrok.io`) and:
1. Update `BASE_URL` in `.env`
2. Set it as webhook in Twilio Console:
   - Go to Twilio Console → WhatsApp → Sandbox Settings
   - Set "When a message comes in" to: `https://your-ngrok-url.ngrok.io/webhook/whatsapp`

### Step 5: Convert Your CSV to Excel

Your data is currently in CSV format. Let's convert it:

```bash
# In the project root directory
python convert_csv_to_excel.py
```

### Step 6: Run the Backend

```bash
cd backend
python app.py
```

The server will start on http://localhost:5000

---

## 📱 Using the System

### 1. Upload Your Lecture Data

Open http://localhost:5000 in your browser, or use the existing frontend at `index.html`.

Use the API to upload your Excel file:
```bash
curl -X POST -F "file=@video_durations_detailed.xlsx" \
  http://localhost:5000/api/upload-excel
```

### 2. Set Your Goals

```bash
curl -X POST http://localhost:5000/api/set-goals \
  -H "Content-Type: application/json" \
  -d '{
    "target_date": "2027-02-07",
    "daily_study_hours": 6,
    "practice_time_percentage": 20,
    "subjects_per_month": [
      {"month": "2026-06", "subjects": ["COA", "OS"]},
      {"month": "2026-07", "subjects": ["TOC", "DL"]},
      {"month": "2026-08", "subjects": ["DSA", "ALGORITHM"]}
    ]
  }'
```

### 3. Start the Scheduler

```bash
curl -X POST http://localhost:5000/api/start-scheduler
```

Now you'll receive daily WhatsApp messages at your specified time!

### 4. Reply to WhatsApp Messages

**Option 1: Voice Message** 🎤
- Record a voice message saying: "I completed COA lecture 1, 2, and 3 today"
- The system will transcribe and extract the lecture numbers

**Option 2: Text Message** 💬
```
Completed COA lecture 1, 2, 3 and OS lecture 5
```

The system will:
1. Extract the completed lectures
2. Update your progress
3. Adjust tomorrow's timetable if needed
4. Send you confirmation and updated goals

---

## 🎯 Example Workflow

### Day 1 (June 8, 2026):
**8:00 PM** - You receive WhatsApp message:
```
🌅 Good Evening! Time for your GATE 2027 progress update!

📚 Today's Goals:
🎥 Lectures to complete: 4
⏱️ Total study time: 3.2 hours (at 2x speed)
📝 Practice time: 0.8 hours

Lectures:
1. COA - Lecture 1
2. COA - Lecture 2
3. COA - Lecture 3
4. COA - Lecture 4

💬 Reply with what you completed!
```

**10:00 PM** - You reply (voice or text):
```
"Hey! I completed COA lectures 1, 2, and 3. 
Lecture 4 was tough, I'll do it tomorrow."
```

**10:01 PM** - System response:
```
✅ Great! I've recorded 3 completed lectures:
• COA - Lecture 1
• COA - Lecture 2
• COA - Lecture 3

📊 You completed 75% of today's goal!
Tomorrow's schedule adjusted slightly to accommodate lecture 4.

Keep it up! 💪
```

### Day 2:
The system automatically adjusts your schedule, moving Lecture 4 to today and slightly reorganizing the rest of the week.

---

## 🎨 Frontend Integration

Your existing `index.html` can be enhanced to show:
- Today's schedule from the API
- Progress statistics
- Upload Excel interface
- Goal setting form

Example API calls from JavaScript:

```javascript
// Get today's timetable
fetch('http://localhost:5000/api/timetable?date=2026-06-08')
  .then(res => res.json())
  .then(data => {
    console.log('Today\'s schedule:', data.schedule);
  });

// Get statistics
fetch('http://localhost:5000/api/stats')
  .then(res => res.json())
  .then(data => {
    console.log('Progress:', data.stats);
  });
```

---

## 🔧 API Endpoints Reference

### Upload Excel
`POST /api/upload-excel`
- Body: FormData with 'file' field
- Returns: Lecture statistics

### Set Goals
`POST /api/set-goals`
- Body: JSON with target_date, daily_study_hours, etc.
- Returns: Generated timetable preview

### Get Timetable
`GET /api/timetable?date=YYYY-MM-DD`
- Returns: Daily schedule for specified date

### Update Progress
`POST /api/update-progress`
- Body: JSON with completed_lectures array
- Returns: Updated timetable and stats

### Get Statistics
`GET /api/stats`
- Returns: Detailed completion statistics

### WhatsApp Webhook
`POST /webhook/whatsapp`
- Automatically called by Twilio
- Handles incoming WhatsApp messages

### Scheduler Control
`POST /api/start-scheduler` - Start daily messages
`POST /api/stop-scheduler` - Stop daily messages

---

## 🎯 Advanced Features

### 1. Smart Lecture Extraction

The system understands multiple formats:
- "Completed COA lecture 1, 2, and 3"
- "Finished OS videos 5 to 10"
- "Did TOC lec 15 and 16"
- "Covered DL lectures from 1 to 5"

### 2. Dynamic Timetable Adjustment

- **Behind Schedule**: Increases daily load by 20%
- **Ahead of Schedule**: Decreases daily load by 10%
- **Practice Time**: Always maintains 20% for practice
- **Flexibility**: Allows ±20% variance in daily study time

### 3. Motivation System

- Random motivational messages 3 times a day
- Weekly progress reports every Sunday
- Streak tracking (consecutive days of completion)

---

## 🐛 Troubleshooting

### "WhatsApp messages not receiving"
- Check Twilio sandbox is active
- Verify webhook URL is correct in Twilio
- Ensure ngrok is running
- Check WhatsApp number format: `whatsapp:+919876543210`

### "Voice messages not transcribing"
- Verify OpenAI API key is correct
- Check API quota hasn't been exceeded
- Ensure audio file format is supported (.ogg, .mp3, .wav)

### "Timetable not generating"
- Verify Excel file has correct columns
- Check target_date is in the future
- Ensure daily_study_hours is reasonable (2-12 hours)

### "Import errors"
- Run: `pip install -r requirements.txt`
- Check Python version is 3.9+

---

##📊 Your Lecture Data Stats

Based on your Excel:
- **Total Lectures**: 659
- **Subjects**: 11 (COA, OS, TOC, DL, DSA, ALGORITHM, COMPILER, CN, DBMS, C PROGRAMMING, APTITUDE)
- **Total Duration**: ~389 hours at 1x speed (~195 hours at 2x speed)
- **Estimated Completion**: With 6 hours/day study, approximately 32 days for lectures + practice time

---

## 🚀 Next Steps

1. **Test the system** with a few manual API calls
2. **Set realistic goals** based on GATE 2027 date (Feb 7, 2027)
3. **Start small** - maybe 4-5 hours daily initially
4. **Be consistent** - reply to WhatsApp messages daily
5. **Adjust as needed** - the system will help you stay on track!

---

## 💡 Pro Tips

1. **Study at 2x speed** for video lectures (system accounts for this)
2. **Do practice immediately** after watching lectures
3. **Reply to WhatsApp** honestly about your progress
4. **Review weekly summaries** to track trends
5. **Adjust goals** if needed - better to complete slowly than burnout

---

## 📞 Support

If you encounter issues:
1. Check the console logs in terminal where Flask is running
2. Check `progress_data.json` for your saved progress
3. Review `.env` file for correct configuration

---

## 🎯 Goal: GATE 2027

**Target Date**: February 7, 2027
**Days Remaining**: ~244 days from today (June 8, 2026)
**Your Success Formula**: Consistency + Smart Planning + This Assistant = GATE Success!

**Let's crush GATE 2027! 💪🎯🔥**

---

*Made with ❤️ for GATE aspirants*
