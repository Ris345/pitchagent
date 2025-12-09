from flask import Flask, request, jsonify
from services.tier1_pacing import analyze_pacing
from services.tier2_coherence import analyze_coherence
from services.tier3_viability import calculate_scores

app = Flask(__name__)

STANDARD_STAGES = ["Intro", "Problem", "Solution", "Business Model", "Market", "Team", "Ask"]

def analyze_progress(current_topic):
    """
    Determine progress based on standard pitch stages.
    """
    if not current_topic:
        return {
            "current_stage": "Unknown",
            "stages_completed": [],
            "stages_missing": STANDARD_STAGES
        }
    
    # Fuzzy match or exact match
    # Simplify: strict match or simple contains
    matched_index = -1
    clean_topic = current_topic.strip()
    
    # Try to find the topic in the list
    for i, stage in enumerate(STANDARD_STAGES):
        if stage.lower() in clean_topic.lower() or clean_topic.lower() in stage.lower():
            matched_index = i
            break
            
    if matched_index != -1:
        return {
            "current_stage": STANDARD_STAGES[matched_index],
            "stages_completed": STANDARD_STAGES[:matched_index],
            "stages_missing": STANDARD_STAGES[matched_index+1:]
        }
    else:
        # If unknown topic, assume it's "custom"
        return {
            "current_stage": clean_topic,
            "stages_completed": [], # Can't guess
            "stages_missing": STANDARD_STAGES # Assume everything standard is still needed? Or just unknown.
        }

@app.route('/analyze', methods=['POST'])
def analyze_pitch():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    try:
        # Extract Inputs
        audio_analysis = data.get('audio_analysis', {})
        video_analysis = data.get('video_analysis', {})
        deck_content = data.get('deck_content', {})
        
        # --- Tier 1: Pacing ---
        current_time = data.get('current_timestamp', 0)
        current_slide = deck_content.get('current_slide_number', 0)
        total_slides = deck_content.get('total_slides', 10) # Default to 10 if missing
        
        tier1_res = analyze_pacing(current_time, current_slide, total_slides)
        
        # --- Tier 2: Coherence ---
        audio_text = audio_analysis.get('transcription', "")
        slide_ocr = deck_content.get('ocr_text', "")
        emotion = video_analysis.get('emotional_tone', "Neutral")
        topic = deck_content.get('slide_topic', "Unknown")
        timestamp_str = f"{int(current_time//60):02d}:{int(current_time%60):02d}"
        
        tier2_res = analyze_coherence(audio_text, slide_ocr, emotion, topic, timestamp_str)
        
        # --- Tier 3: Viability ---
        input_data = {
            "video_analysis": {
                "facial_confidence": video_analysis.get('facial_confidence', 0),
                "eye_contact_percent": video_analysis.get('eye_contact_percent', 0)
            },
            "deck_content": {
                "ocr_text": slide_ocr
            }
        }
        
        tier3_res = calculate_scores(tier1_res, tier2_res, input_data)
        
        # --- Progress Tracking ---
        progress_res = analyze_progress(topic)
        
        # --- Assembling Response ---
        response = {
            "dashboard_status": {
                "overall_score": tier3_res["overall_score"],
                "pacing_signal": tier1_res["pacing_signal"],
                "time_remaining_projection": tier1_res["time_remaining_projection"]
            },
            "tiered_analysis": tier3_res["tiered_analysis"], # Includes coherence, confidence, quality
            "progress_tracker": progress_res,
            "real_time_feedback": tier2_res["real_time_feedback"]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
