
def analyze_pacing(current_timestamp, current_slide, total_slides):
    """
    Tier 1: Progress & Pacing Logic
    
    Args:
        current_timestamp (float): Current time in seconds.
        current_slide (int): Current slide number (1-indexed).
        total_slides (int): Total number of slides.
        
    Returns:
        dict: {
            "pacing_signal": str,
            "time_remaining_projection": str
        }
    """
    TOTAL_TIME_LIMIT = 180.0 # 3 minutes
    
    if current_slide <= 0 or total_slides <= 0:
        return {
            "pacing_signal": "Unknown",
            "time_remaining_projection": "Insufficient data."
        }
        
    # Check if already over time
    if current_timestamp > TOTAL_TIME_LIMIT:
        return {
            "pacing_signal": "Behind Pace", 
            # Prompt uses "Behind Pace" or "Too Slow"? Prompt requested: 'Behind Pace' | 'Perfect' | 'Too Fast'
            "time_remaining_projection": "You have exceeded the time limit."
        }

    # Calculate pacing
    # Ideal pace: timestamp / total_time ~= slide / total_slides
    # Projected finish = (current_timestamp / current_slide) * total_slides
    
    avg_time_per_slide = current_timestamp / current_slide
    projected_total_time = avg_time_per_slide * total_slides
    
    buffer = 20.0 # seconds tolerance
    
    signal = "Perfect"
    projection_msg = "You are on track to finish exactly on time."
    
    if projected_total_time > (TOTAL_TIME_LIMIT + buffer):
        signal = "Behind Pace"
        projection_msg = "At this rate, you will run out of time before the Ask."
    elif projected_total_time < (TOTAL_TIME_LIMIT - buffer):
        signal = "Too Fast"
        projection_msg = "You are speaking too quickly; you might end under time."
    else:
        signal = "Perfect" # Prompt requirement
        projection_msg = "You are well-paced to finish comfortably."
        
    # Heuristic for dwelling on early slides (e.g. Slide 1 > 45s)
    if current_slide == 1 and current_timestamp > 45:
        signal = "Behind Pace"
        projection_msg = "You spent too long on the intro slide."

    return {
        "pacing_signal": signal,
        "time_remaining_projection": projection_msg
    }
