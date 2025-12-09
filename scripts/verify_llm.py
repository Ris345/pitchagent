from services.llm_agent import GravityOrchestrator

def verify_openai():
    print("Verifying Gravity Orchestrator (OpenAI GPT-4o Integration)...")
    orchestrator = GravityOrchestrator()
    
    if not orchestrator.client:
        print("[!] SKIPPED: OPENAI_API_KEY not found in environment.")
        print("    The system is running in HEURISTIC FALLBACK mode.")
        return

    # Mock Data
    audio_data = {"transcription": "We have 100 users.", "wpm": 120}
    video_data = {"facial_confidence": 90, "eye_contact_percent": 90, "emotional_tone": "Happy"}
    deck_data = {
        "current_slide_number": 2, "total_slides": 10, 
        "slide_topic": "Traction", "ocr_text": "Users: 100"
    }
    
    # Run
    print("Sending request to OpenAI...")
    try:
        result = orchestrator.evaluate_pitch(audio_data, video_data, deck_data, current_timestamp=60)
        
        if result:
            print("SUCCESS: Received JSON response from OpenAI GPT-4o.")
            print(result)
        else:
            print("FAILURE: OpenAI returned None or validation failed.")
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    verify_openai()
