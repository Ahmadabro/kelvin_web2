from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        user_message = data.get("message", "").strip()
        audio_data = data.get("audioData", None)
        
        # 1. Immediate fallback for mic input
        if audio_data:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "reply": "🎙️ *[Audio Received]*: Let's calculate the First Law of Thermodynamics ($Q - W = \Delta U$). What parameters are we evaluating?"
            }).encode())
            return

        # 2. Prevent empty submission errors 
        if not user_message:
            user_message = "Hello! Tell me about the First Law of Thermodynamics."

        api_key = os.environ.get("api")
        if not api_key:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Groq API key missing on Vercel."}).encode())
            return

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are KELVIN, a precise AI specialized in Thermodynamics. Answer the user's explicit question directly. Never print setup menus, multiple-choice lists, introduction options, or text templates. Use clear Markdown notation."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": 0.2
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                ai_reply = res_data['choices'][0]['message']['content']

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": ai_reply}).encode())

        except urllib.error.HTTPError as http_err:
            error_body = http_err.read().decode('utf-8')
            self.send_response(http_err.code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Groq Error: {http_err.reason} - {error_body}"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Internal Error: {str(e)}"}).encode())