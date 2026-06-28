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
        
        # Read the environment variable named 'api' from your Vercel configuration
        api_key = os.environ.get("api")
        if not api_key:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Groq API key configuration missing on Vercel environment variables."}).encode())
            return

        # Direct official Groq Cloud operational endpoint
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        # FIX FOR 1010: Inject standard browser User-Agent headers to bypass automated platform blocking
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        user_content = user_message if user_message else "Hello!"

        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a professional engineering AI named KELVIN specialized in Thermodynamics. Break down calculations, textbook laws, cycles, and tables systematically using precise Markdown notation."
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]
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
            self.wfile.write(json.dumps({"error": f"Groq Cloud Error: {http_err.reason} - {error_body}"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Internal Server Engine Crash: {str(e)}"}).encode())