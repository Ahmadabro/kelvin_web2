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
        image_data = data.get("imageData", None)  # Captured base64 data url from client
        audio_data = data.get("audioData", None)  # Captured audio string
        
        api_key = os.environ.get("api")
        if not api_key:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Grok key config missing."}).encode())
            return

        # --- PIPELINE A: HANDLE AUDIO RECORDING (SPEECH-TO-TEXT) ---
        if audio_data:
            # Note: For production university scope project implementations, 
            # you can forward this audio data block directly to a speech processing API.
            # Here we provide a clean mockup echo pipeline to convert speech logic safely.
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"transcription": "[Audio Sample Processed: Explain the First Law of Thermodynamics]"}).encode())
            return

        # --- PIPELINE B: MULTIMODAL TEXT / IMAGE PROCESSING VIA GROK ---
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Base structured message array configuration
        content_payload = []
        if user_message:
            content_payload.append({"type": "text", "text": user_message})
            
        if image_data:
            # Validate and clean standard Data URI prefix formatting structures if present
            if "," in image_data:
                image_data = image_data.split(",")[1]
            content_payload.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                }
            })

        payload = {
            "model": "grok-beta",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a professional engineering AI specialized in Thermodynamics. Analyze code, textbook data snapshots, tables, calculations, or phase change visual layouts comprehensively using clean Markdown."
                },
                {
                    "role": "user",
                    "content": content_payload if image_data else user_message
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

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())