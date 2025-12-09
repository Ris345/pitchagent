import re

def analyze_coherence(audio_text, slide_ocr, facial_emotion, slide_topic, timestamp_str="00:00"):
    """
    Tier 2: Coherence & Sync Analysis
    
    Args:
        audio_text (str): Transcribed text.
        slide_ocr (str): Text content of current slide.
        facial_emotion (str): Detected emotion (e.g., "Happy", "Sad", "Neutral", "Fear").
        slide_topic (str): Context/Topic of slide (e.g., "Market Pain", "Solution").
        timestamp_str (str): Formatted timestamp for feedback.
        
    Returns:
        dict: {
            "coherence_score": int (0-100),
            "real_time_feedback": list[dict]
        }
    """
    feedback = []
    score_deductions = 0
    
    # --- 1. Audio-Visual Sync (Number/Keyword Mismatch) ---
    # Extract numbers (simplified: integers and simple floats like 1.5)
    # Ignore small numbers < 10 to avoid noise? No, "5 competitors" vs "3" is important.
    
    # Regex to find numbers like $1M, 10, 50%, etc.
    # Just extract digits for simple comparison.
    # Logic: if audio has a number NOT present in slide, warn? 
    # Or if slide has a number not in audio?
    # Prompt: "User says 'We have 50k users' but slide says '10k users'"
    # This implies we look for numbers that appear in roughly similar contexts, or just simple set comparison.
    
    def extract_numbers(text):
        if not text: return set()
        # Find all numbers, stripping $ % k M B
        # This is a basic heuristics.
        raw_nums = re.findall(r'\d+(?:\.\d+)?', text)
        return set(raw_nums)

    audio_nums = extract_numbers(audio_text)
    slide_nums = extract_numbers(slide_ocr)
    
    # If there are numbers in both, but NO overlap, we might have a mismatch.
    # Or strict check: if audio has a number X, and slide has number Y, and X != Y, flag.
    # Let's say: if audio triggers a number, check if it's in slide.
    for anum in audio_nums:
        if slide_nums and anum not in slide_nums:
            # Only flag if there are OTHER numbers in the slide (conflict).
            # If slide has no numbers, it's just new info.
            feedback.append({
                "timestamp": timestamp_str,
                "type": "CRITICAL_MISMATCH",
                "message": f"You mentioned '{anum}' but the slide displays values {list(slide_nums)}. Verify your data."
            })
            score_deductions += 20
            
    # --- 2. Emotion-Content Sync ---
    # Define mismatched pairs (Topic -> Invalid Emotions)
    mismatch_map = {
        "Market Pain": ["Happy", "Joy"],
        "Competition": ["Fear", "Uncertainty"],
        "Ask": ["Fear", "Sad"],
        "Team": ["Sad"]
    }
    
    # Normalize inputs
    topic_key = None
    for key in mismatch_map:
        if key.lower() in slide_topic.lower():
            topic_key = key
            break
            
    if topic_key:
        forbidden_emotions = mismatch_map[topic_key]
        if facial_emotion in forbidden_emotions:
            feedback.append({
                "timestamp": timestamp_str,
                "type": "BEHAVIOR_ALERT",
                "message": f"Avoid showing '{facial_emotion}' during the '{topic_key}' section. It sends mixed signals."
            })
            score_deductions += 15

    # Calculate Score
    coherence_score = max(0, 100 - score_deductions)
    
    return {
        "coherence_score": coherence_score,
        "real_time_feedback": feedback
    }
