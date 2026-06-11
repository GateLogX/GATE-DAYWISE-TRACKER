from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class SchedulerService:
    """Schedule daily check-in messages"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.whatsapp = None
        self.timetable_gen = None
        self.current_timetable = None
        self.user_goals = None
    
    def start(self, whatsapp, timetable_gen, current_timetable, user_goals):
        """Start the scheduler"""
        self.whatsapp = whatsapp
        self.timetable_gen = timetable_gen
        self.current_timetable = current_timetable
        self.user_goals = user_goals
        
        # Get scheduled time from environment
        scheduled_time = os.getenv('DAILY_CHECKIN_TIME', '20:00')
        hour, minute = map(int, scheduled_time.split(':'))
        
        # Schedule daily check-in
        self.scheduler.add_job(
            self.send_daily_checkin,
            'cron',
            hour=hour,
            minute=minute,
            id='daily_checkin'
        )
        
        # Schedule weekly summary (every Sunday at 18:00)
        self.scheduler.add_job(
            self.send_weekly_summary,
            'cron',
            day_of_week='sun',
            hour=18,
            minute=0,
            id='weekly_summary'
        )
        
        # Schedule motivation messages (random times during the day)
        self.scheduler.add_job(
            self.send_random_motivation,
            'cron',
            hour='9,14,21',  # 9 AM, 2 PM, 9 PM
            minute=0,
            id='motivation'
        )
        
        self.scheduler.start()
        print(f"Scheduler started. Daily check-in at {scheduled_time}")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("Scheduler stopped")
    
    def send_daily_checkin(self):
        """Send daily check-in message"""
        try:
            if not self.whatsapp or not self.timetable_gen:
                print("Services not initialized")
                return
            
            # Get today's schedule
            today_summary = self.timetable_gen.get_today_summary(self.current_timetable)
            
            # Send WhatsApp message
            self.whatsapp.send_daily_checkin(today_summary)
            
            print(f"Daily check-in sent at {datetime.now()}")
        
        except Exception as e:
            print(f"Error sending daily check-in: {str(e)}")
    
    def send_weekly_summary(self):
        """Send weekly summary"""
        try:
            if not self.whatsapp or not self.timetable_gen:
                return
            
            weekly_summary = self.timetable_gen.get_weekly_summary(self.current_timetable)
            
            message = f"""📊 Weekly Progress Report 📊

{weekly_summary}

Keep up the great work! Remember, consistency is key to cracking GATE 2027! 🎯

Reply 'stats' to see your detailed progress statistics."""
            
            self.whatsapp.send_message(
                os.getenv('YOUR_WHATSAPP_NUMBER'),
                message
            )
            
            print(f"Weekly summary sent at {datetime.now()}")
        
        except Exception as e:
            print(f"Error sending weekly summary: {str(e)}")
    
    def send_random_motivation(self):
        """Send random motivational message"""
        try:
            if not self.whatsapp:
                return
            
            # Only send 30% of the time to avoid being too frequent
            import random
            if random.random() < 0.3:
                self.whatsapp.send_motivation_message()
                print(f"Motivation message sent at {datetime.now()}")
        
        except Exception as e:
            print(f"Error sending motivation: {str(e)}")
    
    def get_status(self):
        """Get scheduler status"""
        if self.scheduler.running:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'next_run': str(job.next_run_time)
                })
            return {
                'running': True,
                'jobs': jobs
            }
        return {'running': False}
