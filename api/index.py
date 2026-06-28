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
        image_data = data.get("imageData", None)
        
        api_key = os.environ.get("api")
        if not api_key:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Groq API key configuration missing on Vercel environment variables."}).encode())
            return

        # Point directly to Groq's official developer cloud endpoint
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Build Groq-compliant content payload
        # Note: Groq supports text prompts universally. (If using vision models later, use llama-3.2-11b-vision-preview)
        content_payload = []
        if user_message:
            content_payload.append({"type": "text", "text": user_message})
        
        if not content_payload:
            content_payload.append({"type": "text", "text": "Hello!"})

        payload = {
            # Utilizing Groq's blazing fast flagship production model
            "model": "llama3-8b-8192",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a professional engineering AI named KELVIN specialized in Thermodynamics. Analyze system code, layouts, cycles, or data calculations comprehensively using precise Markdown notation."
                },
                {
                    "role": "user",
                    "content": content_payload if image_data is None else user_message # fallback to string if text-only for compliance
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
            self.wfile.write(json.dumps({"error": f"Groq API Error: {http_err.reason} - {error_body}"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Internal Script Error: {str(e)}"}).encode())