from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        user_message = data.get("message", "")

        # Target your environment configuration key securely
        api_key = os.environ.get("api")

        if not api_key:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Secret Key variable 'api' missing inside Vercel Dashboard Settings."}).encode())
            return

        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "grok-beta", 
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a professional, high-end engineering AI specialized strictly in Thermodynamics. Break down equations (like ideal gas laws, Clausius-Clapeyron, or Maxwell relations) and processes layout by layout using structured markdown formatting."
                },
                {"role": "user", "content": user_message}
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

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())