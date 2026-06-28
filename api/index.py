from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        user_message = data.get("message", "").strip()
        image_data = data.get("imageData", None)
        audio_data = data.get("audioData", None)
        
        api_key = os.environ.get("api")
        if not api_key:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Grok key configuration missing on Vercel environment variables."}).encode())
            return

        # Handle voice data mock route cleanly
        if audio_data:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"transcription": "[Audio Sample Processed: Explain the First Law of Thermodynamics]"}).encode())
            return

        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Format the user's content payload perfectly matching xAI's developer specs
        if image_data:
            if "," in image_data:
                image_data = image_data.split(",")[1]
            
            # Multimodal payload must be structured as a strict array of objects
            content_payload = []
            if user_message:
                content_payload.append({"type": "text", "text": user_message})
            else:
                content_payload.append({"type": "text", "text": "Analyze this thermodynamics system snapshot."})
                
            content_payload.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                }
            })
            user_content = content_payload
        else:
            # Crucial Fix: Text-only prompts must be sent strictly as a clean, simple string!
            user_content = user_message if user_message else "Hello!"

        payload = {
            "model": "grok-beta",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a professional engineering AI specialized in Thermodynamics. Analyze system code, textbook snapshots, tables, cycles, layouts, or data calculations comprehensively using precise Markdown notation."
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
            # Capture what the remote API screamed back if it fails
            error_body = http_err.read().decode('utf-8')
            self.send_response(http_err.code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"API Error: {http_err.reason} - {error_body}"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Internal Script Error: {str(e)}"}).encode())