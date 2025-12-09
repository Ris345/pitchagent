from flask import Flask, request, jsonify
from services.tier1_pacing import analyze_pacing
from services.tier2_coherence import analyze_coherence
from services.tier3_viability import calculate_scores
from services.llm_agent import GravityOrchestrator
import os

app = Flask(__name__)

# Initialize AI Orchestrator
orchestrator = GravityOrchestrator()

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
        return {
            "current_stage": clean_topic,
            "stages_completed": [], 
            "stages_missing": STANDARD_STAGES 
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
        
        # --- Tier 1: Pacing (Heuristic - keep as truth for time) ---
        current_time = data.get('current_timestamp', 0)
        current_slide = deck_content.get('current_slide_number', 0)
        total_slides = deck_content.get('total_slides', 10) 
        
        tier1_res = analyze_pacing(current_time, current_slide, total_slides)
        
        # --- Tier 2 & 3: Coherence & Viability ---
        # Try LLM first
        llm_result = None
        if orchestrator.client:
             llm_result = orchestrator.evaluate_pitch(
                 audio_analysis, video_analysis, deck_content, current_time
             )
        
        if llm_result:
            # Use LLM results
            tiered_analysis = llm_result.get("tiered_analysis", {})
            real_time_feedback = llm_result.get("real_time_feedback", [])
            
            # Calculate overall score based on LLM sub-scores + Heuristic Pacing
            # We trust LLM content scores, but we trust Heuristic Pacing.
            
            # Extract scores (default to heuristic if missing)
            coherence = tiered_analysis.get("coherence_score", 0)
            confidence = tiered_analysis.get("delivery_confidence", 0)
            quality = tiered_analysis.get("slide_quality", 0)
            
            # Map Pacing Signal to Score
            pacing_map = {"Perfect": 100, "Too Fast": 80, "Behind Pace": 60, "Unknown": 50}
            pacing_score = pacing_map.get(tier1_res["pacing_signal"], 50)
            
            # Weighted Overall Score
            overall_raw = (coherence * 0.4) + (confidence * 0.3) + (pacing_score * 0.2) + (quality * 0.1)
            overall_score = int(overall_raw)
            
            tiered_analysis_final = {
                "coherence_score": coherence,
                "delivery_confidence": confidence,
                "slide_quality": quality
            }
            
        else:
            # Fallback to Heuristic Logic
            print("Using Heuristic Fallback (No LLM or API Key)")
            audio_text = audio_analysis.get('transcription', "")
            slide_ocr = deck_content.get('ocr_text', "")
            emotion = video_analysis.get('emotional_tone', "Neutral")
            topic = deck_content.get('slide_topic', "Unknown")
            timestamp_str = f"{int(current_time//60):02d}:{int(current_time%60):02d}"
            
            tier2_res = analyze_coherence(audio_text, slide_ocr, emotion, topic, timestamp_str)
            
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
            
            overall_score = tier3_res["overall_score"]
            tiered_analysis_final = tier3_res["tiered_analysis"]
            real_time_feedback = tier2_res["real_time_feedback"]
        
        # --- Progress Tracking ---
        topic = deck_content.get('slide_topic', "Unknown")
        progress_res = analyze_progress(topic)
        
        # --- Assembling Response ---
        response = {
            "dashboard_status": {
                "overall_score": overall_score,
                "pacing_signal": tier1_res["pacing_signal"],
                "time_remaining_projection": tier1_res["time_remaining_projection"]
            },
            "tiered_analysis": tiered_analysis_final,
            "progress_tracker": progress_res,
            "real_time_feedback": real_time_feedback
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
