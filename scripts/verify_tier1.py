from services.tier1_pacing import analyze_pacing

def run_tests():
    print("Running manual verification for Tier 1...")
    
    # Test Perfect
    # 10 slides, 18s per slide -> 180s total. Slide 1 @ 18s.
    res = analyze_pacing(18, 1, 10)
    assert res["pacing_signal"] == "Perfect", f"Expected Perfect, got {res['pacing_signal']}"
    print("PASS: Perfect Pace")

    # Test Behind
    # 10 slides. Slide 1 at 30s (proj 300s) -> Behind.
    res = analyze_pacing(30, 1, 10)
    assert res["pacing_signal"] == "Behind Pace", f"Expected Behind Pace, got {res['pacing_signal']}"
    print("PASS: Behind Pace (General)")

    # Test Too Fast
    # 10 slides. Slide 1 at 10s (proj 100s) -> Too Fast.
    res = analyze_pacing(10, 1, 10)
    assert res["pacing_signal"] == "Too Fast", f"Expected Too Fast, got {res['pacing_signal']}"
    print("PASS: Too Fast")
    
    # Test Intro Dwelling
    # Slide 1 > 45s. e.g. 50s.
    res = analyze_pacing(50, 1, 10)
    assert res["pacing_signal"] == "Behind Pace", f"Expected Intro Dwelling -> Behind, got {res['pacing_signal']}"
    assert "intro slide" in res["time_remaining_projection"].lower(), f"Expected dwelling msg, got {res['time_remaining_projection']}"
    print("PASS: Intro Dwelling")
    
    print("All Tier 1 tests passed!")

if __name__ == "__main__":
    run_tests()
