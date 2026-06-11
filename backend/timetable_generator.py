from datetime import datetime, timedelta
import math

class TimetableGenerator:
    """Generate and adjust timetable based on goals and progress"""
    
    def __init__(self):
        self.timetable = {}
    
    def generate_timetable(self, lectures, goals):
        """
        Generate initial timetable based on lectures and goals
        """
        try:
            # Check if lectures data is available
            if not lectures or len(lectures) == 0:
                raise Exception("No lectures data available. Please upload your Excel file first.")
            
            # Calculate total study time available
            start_date = datetime.strptime(goals['start_date'], '%Y-%m-%d')
            target_date = datetime.strptime(goals['target_date'], '%Y-%m-%d')
            days_available = (target_date - start_date).days
            
            daily_study_hours = goals.get('daily_study_hours')
            if daily_study_hours is None:
                raise Exception("Daily study hours is required")
            
            practice_percentage = goals.get('practice_time_percentage', 20) / 100
            
            # Calculate lecture time (accounting for 2x speed)
            total_lecture_seconds = sum(lec['duration_seconds'] for lec in lectures if not lec['completed'])
            total_lecture_hours = (total_lecture_seconds / 3600) / 2  # 2x speed
            
            # Calculate practice time
            practice_hours = total_lecture_hours * (practice_percentage / (1 - practice_percentage))
            
            # Total required hours
            total_required_hours = total_lecture_hours + practice_hours
            
            # Daily allocation
            daily_lecture_hours = daily_study_hours * (1 - practice_percentage)
            daily_practice_hours = daily_study_hours * practice_percentage
            
            # Generate daily schedule
            timetable = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'target_date': target_date.strftime('%Y-%m-%d'),
                'days_available': days_available,
                'total_lecture_hours': round(total_lecture_hours, 2),
                'total_practice_hours': round(practice_hours, 2),
                'total_required_hours': round(total_required_hours, 2),
                'daily_lecture_hours': round(daily_lecture_hours, 2),
                'daily_practice_hours': round(daily_practice_hours, 2),
                'daily_schedule': {},
                'next_7_days': []
            }
            
            # Allocate lectures to days
            current_date = start_date
            lecture_index = 0
            uncompleted_lectures = [lec for lec in lectures if not lec['completed']]
            
            while lecture_index < len(uncompleted_lectures) and current_date <= target_date:
                date_str = current_date.strftime('%Y-%m-%d')
                daily_seconds_target = daily_lecture_hours * 3600 * 2  # 2x speed
                
                day_schedule = {
                    'date': date_str,
                    'lectures': [],
                    'total_lecture_time': 0,
                    'practice_time': daily_practice_hours,
                    'status': 'pending'
                }
                
                current_seconds = 0
                while lecture_index < len(uncompleted_lectures) and current_seconds < daily_seconds_target:
                    lecture = uncompleted_lectures[lecture_index]
                    
                    if current_seconds + lecture['duration_seconds'] <= daily_seconds_target * 1.2:  # 20% flexibility
                        day_schedule['lectures'].append({
                            'subject': lecture['subject'],
                            'video_number': lecture['video_number'],
                            'duration': lecture['duration_formatted'],
                            'file_name': lecture['file_name']
                        })
                        current_seconds += lecture['duration_seconds']
                        lecture_index += 1
                    else:
                        break
                
                day_schedule['total_lecture_time'] = round(current_seconds / 3600 / 2, 2)  # In hours at 2x
                timetable['daily_schedule'][date_str] = day_schedule
                
                # Add to next 7 days if within range
                if (current_date - start_date).days < 7:
                    timetable['next_7_days'].append(day_schedule)
                
                current_date += timedelta(days=1)
            
            self.timetable = timetable
            return timetable
        
        except Exception as e:
            raise Exception(f"Error generating timetable: {str(e)}")
    
    def adjust_timetable(self, current_timetable, completed_lectures, goals):
        """
        Adjust timetable based on actual progress
        """
        try:
            # Get today's date
            today = datetime.now()
            today_str = today.strftime('%Y-%m-%d')
            
            # Calculate if we're behind or ahead
            planned_completion = 0
            actual_completion = len(completed_lectures)
            
            for date_str, schedule in current_timetable['daily_schedule'].items():
                schedule_date = datetime.strptime(date_str, '%Y-%m-%d')
                if schedule_date < today:
                    planned_completion += len(schedule['lectures'])
            
            # Determine adjustment factor
            if actual_completion < planned_completion:
                # Behind schedule - need to increase daily load
                behind_by = planned_completion - actual_completion
                adjustment_factor = 1.2  # Increase daily load by 20%
                print(f"Behind schedule by {behind_by} lectures. Adjusting...")
            elif actual_completion > planned_completion:
                # Ahead of schedule - can reduce daily load
                ahead_by = actual_completion - planned_completion
                adjustment_factor = 0.9  # Decrease daily load by 10%
                print(f"Ahead of schedule by {ahead_by} lectures. Adjusting...")
            else:
                adjustment_factor = 1.0
            
            # Regenerate timetable from today onwards
            adjusted_goals = goals.copy()
            adjusted_goals['start_date'] = today_str
            adjusted_goals['daily_study_hours'] *= adjustment_factor
            
            # Get remaining lectures
            remaining_lectures = []
            for schedule in current_timetable['daily_schedule'].values():
                for lecture in schedule['lectures']:
                    # Check if not completed
                    is_completed = any(
                        comp['subject'] == lecture['subject'] and 
                        comp['video_number'] == lecture['video_number']
                        for comp in completed_lectures
                    )
                    if not is_completed:
                        remaining_lectures.append(lecture)
            
            # Generate new timetable with remaining lectures
            # (This would need the full lecture objects, simplifying for now)
            current_timetable['adjustment_factor'] = adjustment_factor
            current_timetable['last_adjusted'] = today_str
            
            return current_timetable
        
        except Exception as e:
            raise Exception(f"Error adjusting timetable: {str(e)}")
    
    def get_daily_schedule(self, timetable, date_str):
        """Get schedule for a specific date"""
        return timetable['daily_schedule'].get(date_str, {})
    
    def get_today_summary(self, timetable):
        """Get today's schedule summary for WhatsApp message"""
        today_str = datetime.now().strftime('%Y-%m-%d')
        schedule = self.get_daily_schedule(timetable, today_str)
        
        if not schedule or not schedule.get('lectures'):
            return "No lectures scheduled for today. Enjoy your day! 🎉"
        
        summary = f"📚 Today's Goals ({today_str}):\n\n"
        summary += f"🎥 Lectures to complete: {len(schedule['lectures'])}\n"
        summary += f"⏱️ Total study time: {schedule['total_lecture_time']} hours (at 2x speed)\n"
        summary += f"📝 Practice time: {schedule['practice_time']} hours\n\n"
        summary += "Lectures:\n"
        
        for i, lecture in enumerate(schedule['lectures'][:10], 1):  # First 10
            summary += f"{i}. {lecture['subject']} - Lecture {lecture['video_number']}\n"
        
        if len(schedule['lectures']) > 10:
            summary += f"... and {len(schedule['lectures']) - 10} more\n"
        
        return summary
    
    def get_weekly_summary(self, timetable):
        """Get weekly schedule summary"""
        summary = "📅 This Week's Schedule:\n\n"
        
        for day_schedule in timetable.get('next_7_days', []):
            date = datetime.strptime(day_schedule['date'], '%Y-%m-%d')
            day_name = date.strftime('%A')
            
            summary += f"{day_name} ({day_schedule['date']}):\n"
            summary += f"  • {len(day_schedule['lectures'])} lectures\n"
            summary += f"  • {day_schedule['total_lecture_time']} hrs study\n"
            summary += f"  • {day_schedule['practice_time']} hrs practice\n\n"
        
        return summary
