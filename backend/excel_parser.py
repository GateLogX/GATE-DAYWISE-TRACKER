import pandas as pd
from io import BytesIO
from datetime import timedelta

class ExcelParser:
    """Parse Excel file with lecture data"""
    
    def parse_excel(self, file):
        """
        Parse Excel file and extract lecture information
        Expected columns: Subject, Video_Number, Message_ID, Date, 
                         Duration_Seconds, Duration_Formatted, File_Name
        """
        try:
            # Read Excel file
            df = pd.read_excel(file)
            
            # Clean and process data
            lectures = []
            for _, row in df.iterrows():
                lecture = {
                    'subject': str(row['Subject']).strip(),
                    'video_number': int(row['Video_Number']),
                    'duration_seconds': int(row['Duration_Seconds']),
                    'duration_formatted': str(row['Duration_Formatted']),
                    'file_name': str(row['File_Name']),
                    'completed': False,
                    'completion_date': None
                }
                lectures.append(lecture)
            
            return lectures
        
        except Exception as e:
            raise Exception(f"Error parsing Excel: {str(e)}")
    
    def get_statistics(self, lectures):
        """Get statistics from lecture data"""
        if not lectures:
            return {}
        
        # Group by subject
        subjects = {}
        total_duration = 0
        
        for lecture in lectures:
            subject = lecture['subject']
            duration = lecture['duration_seconds']
            
            if subject not in subjects:
                subjects[subject] = {
                    'count': 0,
                    'duration': 0,
                    'duration_hours': 0
                }
            
            subjects[subject]['count'] += 1
            subjects[subject]['duration'] += duration
            subjects[subject]['duration_hours'] = subjects[subject]['duration'] / 3600
            total_duration += duration
        
        return {
            'total_lectures': len(lectures),
            'total_duration_seconds': total_duration,
            'total_duration_hours': round(total_duration / 3600, 2),
            'subjects': subjects,
            'subject_count': len(subjects)
        }
    
    def parse_csv(self, file_path):
        """Parse CSV file (alternative format)"""
        try:
            df = pd.read_csv(file_path)
            return self.parse_excel(BytesIO(df.to_excel(index=False)))
        except Exception as e:
            raise Exception(f"Error parsing CSV: {str(e)}")
