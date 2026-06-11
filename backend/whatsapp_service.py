import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

class WhatsAppService:
    """Handle WhatsApp messaging via Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        self.to_number = os.getenv('YOUR_WHATSAPP_NUMBER')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            print("Warning: Twilio credentials not configured")
    
    def send_message(self, to_number, message):
        """Send WhatsApp message"""
        try:
            if not self.client:
                print(f"[DRY RUN] Would send to {to_number}: {message}")
                return {"success": False, "message": "Twilio not configured"}
            
            # Ensure number has whatsapp: prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            message_obj = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=to_number
            )
            
            print(f"Message sent successfully. SID: {message_obj.sid}")
            return {"success": True, "sid": message_obj.sid}
        
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_daily_checkin(self, timetable_summary):
        """Send daily check-in message"""
        message = f"""📚 Daily Check-in (8 PM) - GATE 2027

{timetable_summary}

✨ Subject Shortcuts:
• c 1,2,3 → C Programming
• dsa 5,6,7 → Data Structures
• algo 10,11 → Algorithms
• coa 1,2,3 → Computer Organization
• os 5,6 → Operating Systems
• dbms 8,9 → Database Management
• cn 1,2 → Computer Networks
• toc 10,11 → Theory of Computation
• compiler 1,2 → Compiler Design
• dl 5,6 → Digital Logic
• dm 1,2,3 → Discrete Math
• math 10,11 → Engineering Math
• apt 1,2 → Aptitude

💡 Reply: "c 15,16,17" or "dsa 20,21,22"
Your tracker will auto-update! ✨"""
        
        return self.send_message(self.to_number, message)
    
    def send_motivation_message(self):
        """Send motivational message"""
        messages = [
            "🔥 Remember: Consistency beats intensity. Keep showing up!",
            "💪 Every lecture completed is one step closer to GATE 2027!",
            "🎯 You're building something great. Trust the process!",
            "⚡ Small progress is still progress. Keep going!",
            "🌟 Your future self will thank you for the work you do today!"
        ]
        
        import random
        message = random.choice(messages)
        return self.send_message(self.to_number, message)
    
    def download_media(self, media_url):
        """Download voice message or media from WhatsApp"""
        try:
            if not self.client:
                return None
            
            import requests
            from requests.auth import HTTPBasicAuth
            
            auth = HTTPBasicAuth(self.account_sid, self.auth_token)
            response = requests.get(media_url, auth=auth)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to download media: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"Error downloading media: {str(e)}")
            return None
