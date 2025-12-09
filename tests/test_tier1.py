import pytest
from services.tier1_pacing import analyze_pacing

def test_analyze_pacing_perfect():
    # 3 slides, 180s total -> 60s per slide. 
    # At slide 1, time 60s -> Perfect
    result = analyze_pacing(60, 1, 3)
    assert result["pacing_signal"] == "Perfect"

def test_analyze_pacing_behind():
    # 3 slides. At slide 1, time 90s -> Projected 270s -> Behind
    result = analyze_pacing(90, 1, 3)
    assert result["pacing_signal"] == "Behind Pace"
    assert "run out of time" in result["time_remaining_projection"]

def test_analyze_pacing_too_fast():
    # 3 slides. At slide 2, time 60s -> 30s/slide -> Projected 90s -> Too Fast
    result = analyze_pacing(60, 2, 3)
    assert result["pacing_signal"] == "Too Fast"

def test_intro_dwelling():
    # Slide 1, 50s (limit 45s) -> Behind Pace
    result = analyze_pacing(50, 1, 10)
    assert result["pacing_signal"] == "Behind Pace"
    assert "intro slide" in result["time_remaining_projection"]

def test_over_time():
    result = analyze_pacing(181, 3, 3)
    assert result["time_remaining_projection"] == "You have exceeded the time limit."
