import os
import openai
from dotenv import load_dotenv
import re
import tempfile

load_dotenv()

class VoiceProcessor:
    """Process voice messages and extract lecture information"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        else:
            print("Warning: OpenAI API key not configured")
    
    def process_voice_message(self, audio_data):
        """
        Convert voice message to text using OpenAI Whisper
        audio_data can be bytes or file path
        """
        try:
            if not self.api_key:
                return "OpenAI API not configured"
            
            # Save audio to temporary file
            if isinstance(audio_data, bytes):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                    temp_file.write(audio_data)
                    temp_path = temp_file.name
            else:
                temp_path = audio_data
            
            # Use OpenAI Whisper API
            with open(temp_path, 'rb') as audio_file:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language="en"  # Can be changed to 'hi' for Hindi
                )
            
            # Clean up temp file
            if isinstance(audio_data, bytes):
                os.unlink(temp_path)
            
            return transcript['text']
        
        except Exception as e:
            print(f"Error processing voice: {str(e)}")
            return f"Error: {str(e)}"
    
    def extract_completed_lectures(self, text, lectures_data, default_subject=None):
        """
        Extract completed lecture information from text
        Supports shortcuts like: c 1,2,3 | coa 5,6 | dsa 10,11
        """
        try:
            completed = []
            text_lower = text.lower()
            
            # Subject shortcuts mapping
            shortcuts = {
                'c': 'C PROGRAMMING',
                'coa': 'COA',
                'os': 'OS',
                'toc': 'TOC',
                'dl': 'DL',
                'dsa': 'DSA',
                'algo': 'ALGORITHM',
                'algorithm': 'ALGORITHM',
                'cn': 'COMPUTER NETWORKS',
                'networks': 'COMPUTER NETWORKS',
                'dbms': 'DBMS',
                'compiler': 'COMPILER DESIGN',
                'dm': 'DISCRETE_MATH',
                'discrete': 'DISCRETE_MATH',
                'math': 'ENGG_MATH',
                'engg': 'ENGG_MATH',
                'aptitude': 'APTITUDE',
                'apt': 'APTITUDE'
            }
            
            # Pattern: "c 1,2,3" or "coa 5,6,7"
            shortcut_pattern = r'\b(' + '|'.join(shortcuts.keys()) + r')\s+([\d,\s]+)'
            shortcut_matches = re.findall(shortcut_pattern, text_lower, re.IGNORECASE)
            
            if shortcut_matches:
                for shortcut, numbers_str in shortcut_matches:
                    subject = shortcuts.get(shortcut.lower())
                    if subject:
                        numbers = re.findall(r'\d+', numbers_str)
                        for num in numbers:
                            video_num = int(num)
                            for lecture in lectures_data:
                                if (lecture['subject'] == subject and 
                                    lecture['video_number'] == video_num):
                                    completed.append(lecture)
                                    break
                return self._remove_duplicates(completed)
            
            # Get unique subjects
            subjects = list(set(lec['subject'] for lec in lectures_data))
            
            # Check if any full subject name is mentioned
            mentioned_subjects = [s for s in subjects if s.lower() in text_lower]
            
            # If no subject mentioned but numbers found, use default_subject
            if not mentioned_subjects:
                all_numbers = re.findall(r'\d+', text)
                if all_numbers:
                    fallback_subject = default_subject if default_subject else (subjects[0] if subjects else None)
                    if fallback_subject:
                        for num in all_numbers:
                            video_num = int(num)
                            for lecture in lectures_data:
                                if (lecture['subject'] == fallback_subject and 
                                    lecture['video_number'] == video_num):
                                    completed.append(lecture)
                                    break
            
            for subject in mentioned_subjects if mentioned_subjects else []:
                subject_lower = subject.lower()
                
                # Check if subject is mentioned
                if subject_lower in text_lower:
                    # Find lecture numbers near the subject mention
                    # Pattern 1: "subject lecture/video X, Y, Z"
                    pattern1 = rf"{subject_lower}.*?(?:lecture|video|lec)s?\s*([\d,\s\-and]+)"
                    matches1 = re.findall(pattern1, text_lower, re.IGNORECASE)
                    
                    for match in matches1:
                        # Extract numbers
                        numbers = re.findall(r'\d+', match)
                        for num in numbers:
                            video_num = int(num)
                            # Find matching lecture
                            for lecture in lectures_data:
                                if (lecture['subject'] == subject and 
                                    lecture['video_number'] == video_num):
                                    completed.append(lecture)
                    
                    # Pattern 2: "lecture X to Y of subject"
                    pattern2 = rf"(?:lecture|video)s?\s*(\d+)\s*(?:to|-)\s*(\d+).*?{subject_lower}"
                    matches2 = re.findall(pattern2, text_lower, re.IGNORECASE)
                    
                    for match in matches2:
                        start, end = int(match[0]), int(match[1])
                        for lecture in lectures_data:
                            if (lecture['subject'] == subject and 
                                start <= lecture['video_number'] <= end):
                                completed.append(lecture)
            
            # Remove duplicates
            return self._remove_duplicates(completed)
        
        except Exception as e:
            print(f"Error extracting lectures: {str(e)}")
            return []
    
    def _remove_duplicates(self, completed):
        """Remove duplicate lectures from list"""
        unique_completed = []
        seen = set()
        for lec in completed:
            key = (lec['subject'], lec['video_number'])
            if key not in seen:
                seen.add(key)
                unique_completed.append(lec)
        return unique_completed
    
    def extract_with_gpt(self, text, lectures_data):
        """
        Use GPT to extract lecture information (more accurate but costs API calls)
        """
        try:
            if not self.api_key:
                return []
            
            # Create a prompt for GPT
            subjects = list(set(lec['subject'] for lec in lectures_data))
            
            prompt = f"""Given the following user message about completed lectures, extract the subject names and lecture numbers.

Available subjects: {', '.join(subjects)}

User message: "{text}"

Return only a JSON array of objects with 'subject' and 'video_number' fields.
Example: [{{"subject": "COA", "video_number": 1}}, {{"subject": "OS", "video_number": 5}}]

If no lectures are mentioned, return an empty array []."""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts lecture information from text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response['choices'][0]['message']['content']
            
            # Parse JSON response
            import json
            extracted = json.loads(result)
            
            # Match with actual lectures
            completed = []
            for item in extracted:
                for lecture in lectures_data:
                    if (lecture['subject'] == item['subject'] and 
                        lecture['video_number'] == item['video_number']):
                        completed.append(lecture)
            
            return completed
        
        except Exception as e:
            print(f"Error with GPT extraction: {str(e)}")
            return self.extract_completed_lectures(text, lectures_data)
