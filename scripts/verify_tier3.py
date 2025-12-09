from services.tier3_viability import calculate_scores

def run_tests():
    print("Running manual verification for Tier 3...")
    
    # Mock inputs
    t1_perfect = {"pacing_signal": "Perfect"}
    t2_perfect = {"coherence_score": 100}
    
    input_perfect = {
        "video_analysis": {"facial_confidence": 100, "eye_contact_percent": 100},
        "deck_content": {"ocr_text": "A perfect amount of text for a slide."} # ~37 chars -> 90 qual
    }
    
    # Exp:
    # Coherence: 100 * 0.4 = 40
    # Conf: 100 * 0.3 = 30
    # Pacing: 100 * 0.2 = 20
    # Slide: 90 * 0.1 = 9
    # Total: 99
    
    res = calculate_scores(t1_perfect, t2_perfect, input_perfect)
    print(f"Overall Score: {res['overall_score']}")
    assert res['overall_score'] == 99, f"Expected 99, got {res['overall_score']}"
    assert res['tiered_analysis']['delivery_confidence'] == 100
    print("PASS: High Score Scenario")
    
    # Low Score Scenario
    t1_bad = {"pacing_signal": "Behind Pace"} # 60 -> 12
    t2_bad = {"coherence_score": 50} # 50 -> 20
    
    input_bad = {
        "video_analysis": {"facial_confidence": 20, "eye_contact_percent": 40}, # Avg 30 -> 9
        "deck_content": {"ocr_text": ""} # 50 -> 5
    }
    
    # Total: 20 + 9 + 12 + 5 = 46
    
    res = calculate_scores(t1_bad, t2_bad, input_bad)
    print(f"Overall Score: {res['overall_score']}")
    assert res['overall_score'] == 46, f"Expected 46, got {res['overall_score']}"
    print("PASS: Low Score Scenario")
    
    print("All Tier 3 tests passed!")

if __name__ == "__main__":
    run_tests()
