
def calculate_scores(tier1_results, tier2_results, input_data):
    """
    Tier 3: Viability Scoring
    
    Args:
        tier1_results (dict): Output from analyze_pacing.
        tier2_results (dict): Output from analyze_coherence.
        input_data (dict): Raw input (audio, video, deck).
        
    Returns:
        dict: {
            "overall_score": int,
            "tiered_analysis": {
                "coherence_score": int,
                "delivery_confidence": int,
                "slide_quality": int
            }
        }
    """
    # 1. Parse Inputs
    pacing_signal = tier1_results.get("pacing_signal", "Unknown")
    coherence_score = tier2_results.get("coherence_score", 0)
    
    video_analysis = input_data.get("video_analysis", {})
    facial_conf = video_analysis.get("facial_confidence", 0)
    eye_contact = video_analysis.get("eye_contact_percent", 0)
    
    deck_content = input_data.get("deck_content", {})
    slide_text = deck_content.get("ocr_text", "")
    
    # 2. Calculate Sub-Scores
    
    # Delivery Confidence
    # Simple average of confidence and eye contact
    delivery_confidence = int((facial_conf + eye_contact) / 2)
    
    # Slide Quality (Heuristic)
    # If text is very short, maybe it's just an image (good?) or empty (bad?)
    # Let's say: 
    # - Empty text: 50
    # - Short text (< 20 chars): 70
    # - Moderate text (20-200 chars): 90
    # - Too much text (> 200 chars): 60 (Busy slide!)
    text_len = len(slide_text)
    if text_len == 0:
        slide_quality = 50
    elif text_len < 20:
        slide_quality = 70
    elif text_len > 200:
        slide_quality = 60
    else:
        slide_quality = 90
        
    # Pacing Score (Internal usage)
    pacing_map = {
        "Perfect": 100,
        "Too Fast": 80,
        "Behind Pace": 60,
        "Unknown": 50
    }
    pacing_score = pacing_map.get(pacing_signal, 50)
    
    # 3. Overall Score
    # Weights: Coherence 40%, Confidence 30%, Pacing 20%, Slide Quality 10%
    overall_raw = (
        (coherence_score * 0.4) +
        (delivery_confidence * 0.3) +
        (pacing_score * 0.2) +
        (slide_quality * 0.1)
    )
    overall_score = int(overall_raw)
    
    return {
        "overall_score": overall_score,
        "tiered_analysis": {
            "coherence_score": coherence_score,
            "delivery_confidence": delivery_confidence,
            "slide_quality": slide_quality
        }
    }
