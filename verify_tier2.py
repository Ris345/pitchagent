from services.tier2_coherence import analyze_coherence

def run_tests():
    print("Running manual verification for Tier 2...")
    
    # Test 1: Perfect Alignment
    res = analyze_coherence(
        audio_text="We have 100 users",
        slide_ocr="Users: 100",
        facial_emotion="Happy",
        slide_topic="Traction"
    )
    assert res["coherence_score"] == 100
    assert len(res["real_time_feedback"]) == 0
    print("PASS: Perfect Alignment")
    
    # Test 2: Number Mismatch
    res = analyze_coherence(
        audio_text="We have 500 users",
        slide_ocr="Users: 100",
        facial_emotion="Happy",
        slide_topic="Traction"
    )
    # Should flag mismatch
    assert res["coherence_score"] < 100
    assert len(res["real_time_feedback"]) == 1
    assert res["real_time_feedback"][0]["type"] == "CRITICAL_MISMATCH"
    print("PASS: Number Mismatch")
    
    # Test 3: Emotion Mismatch
    res = analyze_coherence(
        audio_text="This problem is terrible",
        slide_ocr="Market Pain Points",
        facial_emotion="Happy",
        slide_topic="Market Pain"
    )
    assert res["coherence_score"] < 100
    assert len(res["real_time_feedback"]) == 1
    assert res["real_time_feedback"][0]["type"] == "BEHAVIOR_ALERT"
    print("PASS: Emotion Mismatch")
    
    print("All Tier 2 tests passed!")

if __name__ == "__main__":
    run_tests()
