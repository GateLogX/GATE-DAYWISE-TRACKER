# Add this endpoint after the get_timetable function in app.py:

@app.route('/api/full-timetable', methods=['GET'])
def get_full_timetable():
    """Get complete timetable for all days"""
    try:
        if not current_timetable:
            return jsonify({"error": "No timetable generated yet"}), 400
        
        # Return the full timetable with all days
        all_days = current_timetable.get('schedule', {})
        
        # Convert dict to array format for frontend
        schedule_array = []
        for date_key in sorted(all_days.keys()):
            day_data = all_days[date_key]
            schedule_array.append(day_data)
        
        return jsonify({
            "success": True,
            "total_days": len(schedule_array),
            "timetable": schedule_array,
            "goals": user_goals
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
