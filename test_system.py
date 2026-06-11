#!/usr/bin/env python3
"""
Test the GATE Voice Assistant system
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    if response.status_code == 200:
        print("✅ Server is healthy!")
        print(f"   Response: {response.json()}")
    else:
        print("❌ Server health check failed")
    print()

def test_upload_excel(file_path):
    """Test Excel upload"""
    print("📤 Testing Excel upload...")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/upload-excel", files=files)
            
        if response.status_code == 200:
            data = response.json()
            print("✅ Excel uploaded successfully!")
            print(f"   Total lectures: {data['stats']['total_lectures']}")
            print(f"   Total duration: {data['stats']['total_duration_hours']} hours")
            print(f"   Subjects: {data['stats']['subject_count']}")
            return True
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    print()

def test_set_goals():
    """Test setting goals"""
    print("🎯 Testing goal setting...")
    
    target_date = (datetime.now() + timedelta(days=243)).strftime('%Y-%m-%d')  # GATE 2027
    
    goals = {
        "target_date": target_date,
        "daily_study_hours": 6,
        "practice_time_percentage": 20,
        "start_date": datetime.now().strftime('%Y-%m-%d'),
        "subjects_per_month": [
            {"month": "2026-06", "subjects": ["COA", "OS"]},
            {"month": "2026-07", "subjects": ["TOC", "DL"]},
            {"month": "2026-08", "subjects": ["DSA", "ALGORITHM"]}
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/set-goals",
        json=goals,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Goals set successfully!")
        print(f"   Target date: {target_date}")
        print(f"   Daily study hours: 6 hours")
        print(f"   Timetable generated!")
        return True
    else:
        print(f"❌ Goal setting failed: {response.text}")
        return False
    print()

def test_get_timetable():
    """Test getting timetable"""
    print("📅 Testing timetable retrieval...")
    
    today = datetime.now().strftime('%Y-%m-%d')
    response = requests.get(f"{BASE_URL}/api/timetable?date={today}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Timetable retrieved successfully!")
        schedule = data.get('schedule', {})
        if schedule:
            print(f"   Date: {schedule.get('date')}")
            print(f"   Lectures: {len(schedule.get('lectures', []))}")
            print(f"   Study time: {schedule.get('total_lecture_time')} hours")
            print(f"   Practice time: {schedule.get('practice_time')} hours")
        return True
    else:
        print(f"⚠️  No timetable found (expected if goals not set)")
        return False
    print()

def test_update_progress():
    """Test progress update"""
    print("📝 Testing progress update...")
    
    completed = [
        {"subject": "COA", "video_number": 1, "duration_seconds": 1185},
        {"subject": "COA", "video_number": 2, "duration_seconds": 671}
    ]
    
    response = requests.post(
        f"{BASE_URL}/api/update-progress",
        json={
            "completed_lectures": completed,
            "date": datetime.now().strftime('%Y-%m-%d')
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Progress updated successfully!")
        print(f"   Updated {len(completed)} lectures")
        return True
    else:
        print(f"❌ Progress update failed: {response.text}")
        return False
    print()

def test_get_stats():
    """Test statistics retrieval"""
    print("📊 Testing statistics...")
    
    response = requests.get(f"{BASE_URL}/api/stats")
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get('stats', {})
        print("✅ Statistics retrieved successfully!")
        print(f"   Total completed: {stats.get('total_completed', 0)}")
        print(f"   Overall percentage: {stats.get('overall_percentage', 0)}%")
        return True
    else:
        print(f"⚠️  Statistics not available yet")
        return False
    print()

def run_all_tests(excel_path):
    """Run all tests"""
    print("=" * 60)
    print("🚀 GATE Voice Assistant - Test Suite")
    print("=" * 60)
    print()
    
    # Test 1: Health check
    test_health()
    
    # Test 2: Upload Excel
    if excel_path:
        upload_success = test_upload_excel(excel_path)
        if not upload_success:
            print("⚠️  Skipping remaining tests (upload failed)")
            return
    else:
        print("⚠️  No Excel file provided, skipping upload test")
        print()
    
    # Test 3: Set goals
    test_set_goals()
    
    # Test 4: Get timetable
    test_get_timetable()
    
    # Test 5: Update progress
    test_update_progress()
    
    # Test 6: Get stats
    test_get_stats()
    
    print("=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)
    print()
    print("💡 Next steps:")
    print("1. Set up Twilio WhatsApp sandbox")
    print("2. Configure .env file with your credentials")
    print("3. Start ngrok: ngrok http 5000")
    print("4. Set webhook URL in Twilio console")
    print("5. Start scheduler: POST /api/start-scheduler")
    print("6. Send test WhatsApp message!")
    print()

if __name__ == '__main__':
    import sys
    
    excel_path = None
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    else:
        excel_path = "video_durations_detailed.xlsx"
    
    try:
        run_all_tests(excel_path)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server!")
        print("   Make sure the Flask server is running:")
        print("   cd backend && python app.py")
        sys.exit(1)
