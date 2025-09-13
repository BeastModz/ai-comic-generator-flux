import requests
import json
import logging
from typing import List, Dict
from utils.prompt_templates import PANEL_GENERATION_PROMPT

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
        
    def generate_comic_panels(self, prompt: str, num_panels: int, style: str) -> List[Dict]:
        """Generate panel descriptions from user prompt"""
        
        system_prompt = PANEL_GENERATION_PROMPT.format(
            num_panels=num_panels,
            style=style
        )
        
        user_message = f"Create a {num_panels}-panel comic story based on: {prompt}"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\n{user_message}",
                    "stream": False,
                    "format": "json"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                panels_data = json.loads(result['response'])
                
                # Validate and clean panel data
                panels = []
                for i, panel in enumerate(panels_data.get('panels', [])):
                    panels.append({
                        'index': i,
                        'description': panel.get('description', ''),
                        'dialogue': panel.get('dialogue', ''),
                        'camera_angle': panel.get('camera_angle', 'medium shot'),
                        'emotion': panel.get('emotion', 'neutral')
                    })
                
                logger.info(f"Generated {len(panels)} panel descriptions")
                return panels
                
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to generate panels: {str(e)}")
            # Fallback to simple panel generation
            return self._fallback_panels(prompt, num_panels)
    
    def _fallback_panels(self, prompt: str, num_panels: int) -> List[Dict]:
        """Simple fallback if LLM fails"""
        panels = []
        for i in range(num_panels):
            panels.append({
                'index': i,
                'description': f"Panel {i+1} of story: {prompt}",
                'dialogue': "",
                'camera_angle': 'medium shot',
                'emotion': 'neutral'
            })
        return panels
