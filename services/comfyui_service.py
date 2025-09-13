import json
import requests
from config import COMFYUI_URL

class ComfyUIService:
    def __init__(self, base_url=None):
        self.base_url = base_url or COMFYUI_URL
        
    def is_available(self):
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_status(self):
        try:
            if not self.is_available():
                return {"status": "offline", "message": "ComfyUI server not responding"}
            return {"status": "ready", "message": "Available"}
        except Exception as e:
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def generate_image(self, prompt, style="comic", seed=-1):
        return "test_image.png"
