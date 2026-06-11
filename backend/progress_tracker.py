from datetime import datetime
import json
import os

class ProgressTracker:
    """Track lecture completion progress"""
    
    def __init__(self, data_file='progress_data.json'):
        self.data_file = data_file
        self.completed_lectures = self.load_progress()
    
    def load_progress(self):
        """Load progress from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_progress(self):
        """Save progress to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.completed_lectures, f, indent=2)
        except Exception as e:
            print(f"Error saving progress: {str(e)}")
    
    def add_completed_lectures(self, lectures, date):
        """Add completed lectures"""
        for lecture in lectures:
            # Check if already completed
            exists = any(
                comp['subject'] == lecture['subject'] and 
                comp['video_number'] == lecture['video_number']
                for comp in self.completed_lectures
            )
            
            if not exists:
                completion_record = {
                    'subject': lecture['subject'],
                    'video_number': lecture['video_number'],
                    'completion_date': date,
                    'timestamp': datetime.now().isoformat()
                }
                self.completed_lectures.append(completion_record)
        
        self.save_progress()
    
    def get_all_completed(self):
        """Get all completed lectures"""
        return self.completed_lectures
    
    def get_stats(self):
        """Get completion statistics"""
        total = len(self.completed_lectures)
        
        # Group by subject
        by_subject = {}
        by_date = {}
        
        for comp in self.completed_lectures:
            subject = comp['subject']
            date = comp['completion_date']
            
            by_subject[subject] = by_subject.get(subject, 0) + 1
            by_date[date] = by_date.get(date, 0) + 1
        
        # Get recent activity (last 7 days)
        recent_dates = sorted(by_date.keys(), reverse=True)[:7]
        recent_activity = {date: by_date[date] for date in recent_dates}
        
        return {
            'total_completed': total,
            'by_subject': by_subject,
            'recent_activity': recent_activity,
            'subjects_completed': len(by_subject)
        }
    
    def get_detailed_stats(self, all_lectures):
        """Get detailed statistics including percentage completion"""
        stats = self.get_stats()
        
        # Calculate total lectures per subject
        subject_totals = {}
        total_duration = 0
        completed_duration = 0
        
        for lecture in all_lectures:
            subject = lecture['subject']
            subject_totals[subject] = subject_totals.get(subject, 0) + 1
            total_duration += lecture['duration_seconds']
        
        # Calculate completed duration
        for comp in self.completed_lectures:
            for lecture in all_lectures:
                if (lecture['subject'] == comp['subject'] and 
                    lecture['video_number'] == comp['video_number']):
                    completed_duration += lecture['duration_seconds']
                    break
        
        # Calculate percentages
        subject_percentages = {}
        for subject, completed_count in stats['by_subject'].items():
            total_count = subject_totals.get(subject, 0)
            if total_count > 0:
                subject_percentages[subject] = {
                    'completed': completed_count,
                    'total': total_count,
                    'percentage': round((completed_count / total_count) * 100, 2)
                }
        
        overall_percentage = 0
        if len(all_lectures) > 0:
            overall_percentage = round((len(self.completed_lectures) / len(all_lectures)) * 100, 2)
        
        return {
            'total_lectures': len(all_lectures),
            'completed_lectures': len(self.completed_lectures),
            'overall_percentage': overall_percentage,
            'total_duration_hours': round(total_duration / 3600, 2),
            'completed_duration_hours': round(completed_duration / 3600, 2),
            'by_subject': subject_percentages,
            'recent_activity': stats['recent_activity']
        }
    
    def is_lecture_completed(self, subject, video_number):
        """Check if a specific lecture is completed"""
        return any(
            comp['subject'] == subject and 
            comp['video_number'] == video_number
            for comp in self.completed_lectures
        )
    
    def get_completion_streak(self):
        """Calculate current completion streak (consecutive days)"""
        if not self.completed_lectures:
            return 0
        
        # Get unique dates and sort
        dates = sorted(set(comp['completion_date'] for comp in self.completed_lectures))
        
        if not dates:
            return 0
        
        # Check for consecutive days
        streak = 1
        for i in range(len(dates) - 1, 0, -1):
            date1 = datetime.strptime(dates[i], '%Y-%m-%d')
            date2 = datetime.strptime(dates[i-1], '%Y-%m-%d')
            diff = (date1 - date2).days
            
            if diff == 1:
                streak += 1
            else:
                break
        
        return streak
