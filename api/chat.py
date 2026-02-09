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
        try:
            # Read request
            content_length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(content_length)
            data = json.loads(raw_data)
            user_prompt = data.get('prompt', '(no prompt sent)')

            # ── Diagnostics ─────────────────────────────────────
            debug_info = {
                "received_prompt": user_prompt,
                "api_key_exists": "GEMINI_API_KEY" in os.environ,
                "api_key_value": os.environ.get("GEMINI_API_KEY", "NOT_FOUND")[:6] + "...",
                "genai_imported": genai is not None,
            }

            if not genai:
                raise ImportError(f"google.generativeai import failed: {import_error}")

            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is missing or empty")

            genai.configure(api_key=api_key)

            # Use a known working model name
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',   # ← very reliable in 2026
                # system_instruction=SYSTEM_PROMPT   # comment out for now to isolate
            )

            # Simple generation test
            response = model.generate_content(user_prompt)
            reply_text = response.text.strip()

            debug_info["generation_success"] = True

        except Exception as e:
            reply_text = "I'm sorry, something broke on my end."
            debug_info = debug_info if 'debug_info' in locals() else {}
            debug_info.update({
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "generation_success": False
            })

        # ── Send response ───────────────────────────────────
        self.send_response(200 if 'error_type' not in debug_info else 200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        final_response = {
            "text": reply_text,
            "debug": debug_info   # ← this will show in your browser console / network tab
        }
        self.wfile.write(json.dumps(final_response).encode('utf-8'))
            
            error_msg = f"Error: {str(e)}"
            self.wfile.write(json.dumps({'error': error_msg}).encode('utf-8'))
