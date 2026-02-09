from http.server import BaseHTTPRequestHandler
import json
import os
import traceback

try:
    import google.generativeai as genai
except ImportError as e:
    genai = None
    import_error = str(e)

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        debug_lines = []  # Collect debug messages here
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(content_length)
            data = json.loads(raw_data)
            user_prompt = data.get('prompt', '(no prompt sent)')
            
            debug_lines.append(f"Received prompt: {user_prompt}")
            debug_lines.append(f"API key exists? {'Yes' if 'GEMINI_API_KEY' in os.environ else 'NO'}")
            api_key_preview = os.environ.get("GEMINI_API_KEY", "NOT_FOUND")[:10] + "..." if os.environ.get("GEMINI_API_KEY") else "NOT_FOUND"
            debug_lines.append(f"API key preview: {api_key_preview}")
            debug_lines.append(f"google.generativeai imported? {'Yes' if genai is not None else 'NO'}")
            
            if not genai:
                raise ImportError(f"google.generativeai import failed: {import_error}")
            
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is missing or empty")
            
            genai.configure(api_key=api_key)
            
            # Use a currently valid model (as of Feb 2026 - gemini-1.5-flash is stable and widely available)
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                # system_instruction=SYSTEM_PROMPT  # Uncomment later once basic works
            )
            
            response = model.generate_content(user_prompt)
            reply_text = response.text.strip()
            
            debug_lines.append("Generation SUCCESS!")
        
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            tb = traceback.format_exc()
            
            debug_lines.append("ERROR OCCURRED!")
            debug_lines.append(f"Type: {error_type}")
            debug_lines.append(f"Message: {error_msg}")
            debug_lines.append(f"Traceback: {tb[:500]}...")  # Truncate long tracebacks
            
            reply_text = "I'm sorry, something broke on my end.\n\nDebug info (for troubleshooting):\n" + "\n".join(debug_lines)
        
        # Always send 200 so browser shows the text (Vercel 500 hides body sometimes)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        final_response = {"text": reply_text}
        self.wfile.write(json.dumps(final_response).encode('utf-8'))
