from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        info = {
            "google_key_exists": "GOOGLE_API_KEY" in os.environ,
            "google_key_preview": os.environ.get("GOOGLE_API_KEY", "NOT_SET")[:12] + "..." if os.environ.get("GOOGLE_API_KEY") else "NOT_SET",
            "gemini_key_exists": "GEMINI_API_KEY" in os.environ,
            "all_env_keys": list(os.environ.keys())[:30],
            "vercel_env": os.environ.get("VERCEL_ENV", "not_set"),
            "python_version": os.environ.get("PYTHON_VERSION", "not_set")
        }

        self.wfile.write(json.dumps(info, indent=2).encode('utf-8'))
