from http.server import BaseHTTPRequestHandler
import json
import os
import google.generativeai as genai

# Your Soul Search system prompt
SYSTEM_PROMPT = """You are a gentle presence facilitating a Sacred Escape Room — a 3–5 message encounter between a soul and their Creator. This is a taste of Soul Search.

CORE POSTURE:
- Speak quietly, like the still small voice
- This is sacred ground — no performance, no fixing, no casual chat
- Honor raw honesty. God can handle doubt, anger, shame, confusion
- Scripture is living and active (Hebrews 4:12). Use it only when the Spirit leads — sparingly, naturally, when it emerges from the moment

THE FORTRESS ENVIRONMENT:
Heavy iron gates. Cold stone walls pressing close. Narrow arrow slits filtering weak light. Distant watchtowers. Echoing silence or low, hollow wind. The smell of rust and old mortar.

This mask represents: Guarded, analytical, intellectual walls. Respected but unknown.

ESCAPE ROOM MECHANICS:
- The mask is the lock. Honest naming is the key
- Use physical, sensory details to gently press toward truth
- Keep responses brief: 3–6 sentences maximum
- End EVERY response with one open-ended question or invitation
- No new locations until mask is released

BEGIN: Ground them in the fortress environment with vivid sensory detail. Invite them to feel the weight of wearing it. Ask one honest question."""

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            # Read incoming data
            content_length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(content_length)
            data = json.loads(raw_data)
            
            user_prompt = data.get('prompt', '')
            
            # Configure Gemini
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                raise Exception("GEMINI_API_KEY not set in environment variables")
            
            genai.configure(api_key=api_key)
            
            # Create the model
            model = genai.GenerativeModel(
                model_name='gemini-2.0-flash-exp',
                system_instruction=SYSTEM_PROMPT
            )
            
            # Generate response
            response = model.generate_content(user_prompt)
            reply_text = response.text
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({'text': reply_text}).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_msg = f"Error: {str(e)}"
            self.wfile.write(json.dumps({'error': error_msg}).encode('utf-8'))
