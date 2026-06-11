from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import json

# Import our modules
# Updated: 2026-06-12 - 4 hours/day schedule
from excel_parser import ExcelParser
from timetable_generator import TimetableGenerator
from whatsapp_service import WhatsAppService
from voice_processor import VoiceProcessor
from progress_tracker import ProgressTracker
from scheduler_service import SchedulerService
from github_sync import GitHubSync

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize GitHub sync
github_sync = GitHubSync()

# Initialize services
excel_parser = ExcelParser()
timetable_gen = TimetableGenerator()
whatsapp = WhatsAppService()
voice_processor = VoiceProcessor()
progress_tracker = ProgressTracker()
scheduler = SchedulerService()

# Store uploaded data - with persistence
DATA_FILE = 'app_data.json'

def load_app_data():
    """Load persisted app data"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return data.get('lectures_data', []), data.get('user_goals', {}), data.get('current_timetable', {})
    except Exception as e:
        print(f"Error loading app data: {e}")
    return [], {}, {}

def save_app_data():
    """Save app data to persist across restarts"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({
                'lectures_data': lectures_data,
                'user_goals': user_goals,
                'current_timetable': current_timetable
            }, f, indent=2)
        print("App data saved successfully")
        # Note: app_data.json is tracked in Git and restored on deployment
        # We don't auto-commit it to avoid deployment loops
    except Exception as e:
        print(f"Error saving app data: {e}")

# Load persisted data on startup
lectures_data, user_goals, current_timetable = load_app_data()
print(f"✅ Loaded {len(lectures_data)} lectures from storage")
print(f"📚 Daily study hours: {user_goals.get('daily_study_hours', 'NOT SET')} hours/day")
print(f"📅 Timetable days: {len(current_timetable.get('daily_schedule', {}))} days")
print(f"🔧 App version: 2026-06-12-4hrs-120days")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    """Upload and parse Excel file with lecture data"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Parse Excel file
        global lectures_data
        lectures_data = excel_parser.parse_excel(file)
        
        # Save data
        save_app_data()
        
        # Get statistics
        stats = excel_parser.get_statistics(lectures_data)
        
        return jsonify({
            "success": True,
            "message": f"Successfully parsed {len(lectures_data)} lectures",
            "stats": stats,
            "lectures": lectures_data[:10]  # Send first 10 as preview
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/set-goals', methods=['POST'])
def set_goals():
    """Set user goals for completion"""
    try:
        data = request.json
        print(f"Received data: {data}")  # Debug log
        
        global user_goals
        # Ensure we have valid values
        daily_hours = data.get('daily_study_hours')
        if daily_hours is not None:
            daily_hours = float(daily_hours) if daily_hours != '' else 6
        else:
            daily_hours = 6
            
        practice_pct = data.get('practice_time_percentage')
        if practice_pct is not None:
            practice_pct = float(practice_pct) if practice_pct != '' else 20
        else:
            practice_pct = 20
        
        user_goals = {
            "target_date": data.get('target_date'),  # GATE 2027 date
            "subjects_per_month": data.get('subjects_per_month', []),
            "daily_study_hours": daily_hours,
            "practice_time_percentage": practice_pct,
            "start_date": data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        }
        print(f"Processed goals: {user_goals}")  # Debug log
        
        # Generate initial timetable
        global current_timetable
        current_timetable = timetable_gen.generate_timetable(
            lectures_data, 
            user_goals
        )
        
        # Save data
        save_app_data()
        
        return jsonify({
            "success": True,
            "message": "Goals set successfully",
            "goals": user_goals,
            "timetable_preview": current_timetable.get('next_7_days', [])
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/timetable', methods=['GET'])
def get_timetable():
    """Get current timetable"""
    try:
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if not current_timetable:
            return jsonify({"error": "No timetable generated yet"}), 400
        
        daily_schedule = timetable_gen.get_daily_schedule(current_timetable, date_str)
        
        return jsonify({
            "success": True,
            "date": date_str,
            "schedule": daily_schedule,
            "completion_stats": progress_tracker.get_stats()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/full-timetable', methods=['GET'])
def get_full_timetable():
    """Get complete timetable for all days"""
    try:
        if not current_timetable:
            return jsonify({"error": "No timetable generated yet"}), 400
        
        # Return the full timetable with all days
        all_days = current_timetable.get('daily_schedule', {})
        
        # Convert dict to array format for frontend
        schedule_array = []
        day_number = 1
        for date_key in sorted(all_days.keys()):
            day_data = all_days[date_key]
            
            # Transform backend format to frontend format
            videos = []
            total_seconds = 0
            
            # Extract subject from first lecture (assumes all lectures in a day are same subject)
            subject = day_data.get('lectures', [{}])[0].get('subject', 'UNKNOWN') if day_data.get('lectures') else 'UNKNOWN'
            
            for lecture in day_data.get('lectures', []):
                # Parse duration to seconds (handle different formats)
                duration_str = lecture.get('duration', '00:00:00')
                try:
                    # Try parsing as HH:MM:SS
                    parts = duration_str.split(':')
                    if len(parts) == 3:
                        h, m, s = parts
                        seconds = int(h) * 3600 + int(m) * 60 + int(s)
                    else:
                        seconds = 0
                except:
                    seconds = 0
                
                total_seconds += seconds
                
                # Create video object matching frontend format
                videos.append({
                    'subject': lecture.get('subject', ''),
                    'videoNumber': str(lecture.get('video_number', '')),
                    'fileName': lecture.get('file_name', ''),
                    'durationSeconds': seconds,
                    'messageId': f"{lecture.get('subject', '')}_{lecture.get('video_number', '')}"
                })
            
            schedule_array.append({
                'day': day_number,
                'subject': subject,
                'videos': videos,
                'totalSeconds': total_seconds,
                'totalHours': round(total_seconds / 3600, 2),
                'originalHours': round((total_seconds * 2) / 3600, 2)
            })
            day_number += 1
        
        return jsonify({
            "success": True,
            "total_days": len(schedule_array),
            "timetable": schedule_array,
            "goals": user_goals
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/update-progress', methods=['POST'])
def update_progress():
    """Manually update progress"""
    try:
        data = request.json
        completed_lectures = data.get('completed_lectures', [])
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Update progress
        progress_tracker.add_completed_lectures(completed_lectures, date)
        
        # Regenerate timetable with updated progress
        global current_timetable
        current_timetable = timetable_gen.adjust_timetable(
            current_timetable,
            progress_tracker.get_all_completed(),
            user_goals
        )
        
        return jsonify({
            "success": True,
            "message": f"Updated {len(completed_lectures)} lectures",
            "updated_timetable": current_timetable.get('next_7_days', []),
            "stats": progress_tracker.get_stats()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    try:
        # Get message data from Twilio
        from_number = request.form.get('From')
        message_body = request.form.get('Body')
        media_url = request.form.get('MediaUrl0')  # Voice message URL
        
        print(f"Received message from {from_number}: {message_body}")
        
        # Check if it's a voice message
        if media_url:
            # Process voice message
            transcription = voice_processor.process_voice_message(media_url)
            print(f"Transcription: {transcription}")
            
            # Extract completed lectures from transcription
            completed_lectures = voice_processor.extract_completed_lectures(
                transcription, 
                lectures_data
            )
            
            if completed_lectures:
                # Update progress
                progress_tracker.add_completed_lectures(
                    completed_lectures, 
                    datetime.now().strftime('%Y-%m-%d')
                )
                
                # Adjust timetable
                global current_timetable
                current_timetable = timetable_gen.adjust_timetable(
                    current_timetable,
                    progress_tracker.get_all_completed(),
                    user_goals
                )
                
                # Send confirmation
                response_msg = f"✅ Great! I've recorded {len(completed_lectures)} completed lectures:\n"
                for lec in completed_lectures[:5]:  # Show first 5
                    response_msg += f"• {lec['subject']} - Lecture {lec['video_number']}\n"
                
                response_msg += f"\n📊 Today's updated goals:\n{timetable_gen.get_today_summary(current_timetable)}"
                
                whatsapp.send_message(from_number.replace('whatsapp:', ''), response_msg)
            else:
                whatsapp.send_message(
                    from_number.replace('whatsapp:', ''), 
                    "I couldn't understand the lectures you mentioned. Please try again with lecture numbers or names."
                )
        
        elif message_body:
            # Handle text message - determine subject from today's schedule
            today = datetime.now().strftime('%Y-%m-%d')
            today_subject = None
            
            # Get today's scheduled subject from timetable
            if current_timetable and 'daily_schedule' in current_timetable:
                today_schedule = current_timetable['daily_schedule'].get(today, {})
                lectures_today = today_schedule.get('lectures', [])
                if lectures_today:
                    # Use the most common subject in today's schedule
                    subjects_today = [lec['subject'] for lec in lectures_today]
                    if subjects_today:
                        today_subject = max(set(subjects_today), key=subjects_today.count)
            
            # Extract lectures with context
            completed_lectures = voice_processor.extract_completed_lectures(
                message_body, 
                lectures_data,
                default_subject=today_subject
            )
            
            if completed_lectures:
                progress_tracker.add_completed_lectures(
                    completed_lectures, 
                    datetime.now().strftime('%Y-%m-%d')
                )
                
                whatsapp.send_message(
                    from_number.replace('whatsapp:', ''), 
                    f"✅ Recorded {len(completed_lectures)} lectures!"
                )
        
        return jsonify({"success": True})
    
    except Exception as e:
        print(f"Error in webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get completion statistics"""
    try:
        stats = progress_tracker.get_detailed_stats(lectures_data)
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Get detailed progress data with completed lectures list"""
    try:
        completed = progress_tracker.get_all_completed_lectures()
        return jsonify({
            "success": True,
            "completed_lectures": completed
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/start-scheduler', methods=['POST'])
def start_scheduler():
    """Start the daily check-in scheduler"""
    try:
        scheduler.start(whatsapp, timetable_gen, current_timetable, user_goals)
        return jsonify({
            "success": True,
            "message": "Scheduler started. You'll receive daily WhatsApp messages."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stop-scheduler', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler"""
    try:
        scheduler.stop()
        return jsonify({
            "success": True,
            "message": "Scheduler stopped."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-whatsapp', methods=['POST'])
def test_whatsapp():
    """Send a test WhatsApp message"""
    try:
        data = request.json or {}
        message = data.get('message', '🎯 Test message from GATE Assistant!')
        
        # Get the user's WhatsApp number from .env
        to_number = os.getenv('YOUR_WHATSAPP_NUMBER')
        
        result = whatsapp.send_message(to_number, message)
        
        if result.get('success'):
            return jsonify({
                "success": True,
                "message": "Test WhatsApp message sent successfully! Check your phone.",
                "details": result
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', 'Failed to send message'),
                "details": result
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reorder-subjects', methods=['POST'])
def reorder_subjects():
    """Reorder subjects and regenerate timetable"""
    global lectures_data, current_timetable
    
    try:
        data = request.json
        subject_order = data.get('subject_order', [])
        
        if not lectures_data:
            return jsonify({"error": "No lectures data available. Please upload Excel file first."}), 400
        
        if not user_goals:
            return jsonify({"error": "No goals set. Please set your goals first."}), 400
        
        # Reorder lectures based on subject priority
        ordered_lectures = []
        
        # First add lectures from prioritized subjects
        for subject in subject_order:
            subject_lectures = [lec for lec in lectures_data if lec['subject'] == subject]
            ordered_lectures.extend(subject_lectures)
        
        # Then add any remaining lectures not in the priority list
        remaining_lectures = [lec for lec in lectures_data if lec['subject'] not in subject_order]
        ordered_lectures.extend(remaining_lectures)
        
        lectures_data = ordered_lectures
        
        # Regenerate timetable with new order
        current_timetable = timetable_gen.generate_timetable(lectures_data, user_goals)
        
        # Save data
        save_app_data()
        
        return jsonify({
            "success": True,
            "message": f"Subjects reordered. {subject_order[0]} will be covered first!",
            "timetable": current_timetable
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
