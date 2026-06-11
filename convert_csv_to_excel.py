#!/usr/bin/env python3
"""
Convert CSV lecture data to Excel format for the voice assistant
"""

import pandas as pd
import sys

def convert_csv_to_excel(csv_file='video_durations_detailed.csv', 
                         excel_file='video_durations_detailed.xlsx'):
    """Convert CSV to Excel"""
    try:
        print(f"Reading {csv_file}...")
        df = pd.read_csv(csv_file)  # Comma-separated
        
        print(f"Found {len(df)} lectures")
        print(f"Subjects: {df['Subject'].unique()}")
        
        # Save to Excel
        print(f"Saving to {excel_file}...")
        df.to_excel(excel_file, index=False)
        
        print(f"✅ Successfully converted to {excel_file}")
        
        # Print statistics
        print("\n📊 Statistics:")
        print(f"Total Lectures: {len(df)}")
        print(f"Total Duration: {df['Duration_Seconds'].sum() / 3600:.2f} hours")
        print(f"\nLectures per subject:")
        for subject, count in df['Subject'].value_counts().items():
            subject_duration = df[df['Subject'] == subject]['Duration_Seconds'].sum() / 3600
            print(f"  {subject}: {count} lectures ({subject_duration:.2f} hours)")
        
        return excel_file
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        excel_file = sys.argv[2] if len(sys.argv) > 2 else 'output.xlsx'
        convert_csv_to_excel(csv_file, excel_file)
    else:
        convert_csv_to_excel()
