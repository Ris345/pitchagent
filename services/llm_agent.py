import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GravityOrchestrator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            print("WARNING: OPENAI_API_KEY not found. LLM features will be disabled.")
            self.client = None

    def evaluate_pitch(self, audio_data, video_data, deck_data, current_timestamp, total_time_limit=180):
        """
        Orchestrates the multi-modal analysis using OpenAI GPT-4o.
        Returns a dictionary matching the specific JSON schema required by the specialized dashboard.
        """
        if not self.client:
            return None

        # 1. Construct the Context
        context = {
            "current_timestamp": current_timestamp,
            "total_time_limit": total_time_limit,
            "audio_transcription": audio_data.get("transcription", ""),
            "detected_wpm": audio_data.get("wpm", 0),
            "visual_signals": {
                "facial_confidence": video_data.get("facial_confidence", 0),
                "eye_contact": video_data.get("eye_contact_percent", 0),
                "emotion": video_data.get("emotional_tone", "Unknown")
            },
            "slide_context": {
                "number": deck_data.get("current_slide_number", 0),
                "total": deck_data.get("total_slides", 0),
                "topic": deck_data.get("slide_topic", "Unknown"),
                "ocr_text": deck_data.get("ocr_text", "")
            }
        }
        
        json_context = json.dumps(context, indent=2)

        # 2. System Prompt
        system_prompt = """
        You are the Gravity Pitch Architect, an expert investor AI.
        Analyze the following real-time pitch data stream and output a STRICT JSON assessment.
        
        YOUR TASK:
        1. Analyze **Coherence**: Does the spoken transcript match the slide text? (Check for number mismatches, e.g. "We have 50 users" vs Slide "100 users").
        2. Analyze **Emotion Sync**: Is the user's emotion appropriate for the topic? (e.g. Smiling during "Pain Points" is bad).
        3. Analyze **Viability**: Score the pitch quality based on confidence, clarity, and content.
        
        OUTPUT SCHEMA (STRICT JSON ONLY):
        {
          "tiered_analysis": {
            "coherence_score": [0-100],
            "delivery_confidence": [0-100],
            "slide_quality": [0-100]
          },
          "real_time_feedback": [
             { "timestamp": "current_time_str", "type": "CRITICAL_MISMATCH" | "BEHAVIOR_ALERT" | "KUDOS", "message": "Short, punchy feedback." }
          ]
        }
        
        If there are no alerts, "real_time_feedback" should be an empty list.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the pitch data context:\n{json_context}"}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"LLM Error: {e}")
            return None
