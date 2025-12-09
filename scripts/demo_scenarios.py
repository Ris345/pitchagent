from app import app
import json

def run_demo():
    client = app.test_client()
    
    scenarios = [
        {
            "name": "The Perfect Pitch",
            "payload": {
                "current_timestamp": 60,
                "audio_analysis": {"transcription": "We are growing fast.", "wpm": 130},
                "video_analysis": {"facial_confidence": 95, "eye_contact_percent": 90, "emotional_tone": "Happy"},
                "deck_content": {
                    "current_slide_number": 3, "total_slides": 9, 
                    "slide_topic": "Problem", "ocr_text": "The Problem is huge."
                }
            }
        },
        {
            "name": "The Rushed Panic",
            "payload": {
                "current_timestamp": 30, # Way too fast for slide 5
                "audio_analysis": {"transcription": "Quickly moving on...", "wpm": 200},
                "video_analysis": {"facial_confidence": 30, "eye_contact_percent": 20, "emotional_tone": "Fear"},
                "deck_content": {
                    "current_slide_number": 5, "total_slides": 10, 
                    "slide_topic": "Business Model", "ocr_text": "Revenue"
                }
            }
        },
        {
            "name": "The Data Discrepancy",
            "payload": {
                "current_timestamp": 100,
                "audio_analysis": {"transcription": "We have $5M revenue.", "wpm": 120},
                "video_analysis": {"facial_confidence": 80, "eye_contact_percent": 80, "emotional_tone": "Neutral"},
                "deck_content": {
                    "current_slide_number": 6, "total_slides": 10,
                    "slide_topic": "Traction", "ocr_text": "Revenue: $1M" # Mismatch $5M vs $1M
                }
            }
        }
    ]
    
    print(f"{'='*60}")
    print(f"GRAVITY PITCH ARCHITECT - DEMO RUN")
    print(f"{'='*60}\n")
    
    for sc in scenarios:
        print(f"--- SCENARIO: {sc['name']} ---")
        response = client.post('/analyze', data=json.dumps(sc['payload']), content_type='application/json')
        data = response.get_json()
        
        # Pretty print key parts
        print(f"STATUS: {data['dashboard_status']['pacing_signal']} (Score: {data['dashboard_status']['overall_score']})")
        print(f"MSG: {data['dashboard_status']['time_remaining_projection']}")
        
        if data['real_time_feedback']:
            print("ALERTS:")
            for alert in data['real_time_feedback']:
                 print(f"  [!] {alert['type']}: {alert['message']}")
        else:
            print("ALERTS: None")
        print("\n")

if __name__ == "__main__":
    run_demo()
