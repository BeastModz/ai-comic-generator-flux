"""
ComfyUI Service
Handles communication with ComfyUI API for image generation
"""

import json
import uuid
import time
import requests
import logging
import random
from config import COMFYUI_URL, COMFYUI_WORKFLOW

logger = logging.getLogger(__name__)

class ComfyUIService:
    def __init__(self, base_url=None):
        self.base_url = base_url or COMFYUI_URL
        self.workflow_path = COMFYUI_WORKFLOW
        
    def is_available(self):
        """Check if ComfyUI server is running"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_status(self):
        """Get ComfyUI server status"""
        try:
            if not self.is_available():
                return {"status": "offline", "message": "ComfyUI server not responding"}
            return {"status": "ready", "message": "Available"}
        except Exception as e:
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def generate_image(self, prompt, style="comic", seed=-1):
        """Generate an image using ComfyUI"""
        try:
            logger.info(f"Starting image generation for prompt: {prompt[:50]}...")
            
            # Load workflow
            workflow = self._load_workflow()
            if not workflow:
                raise Exception("Failed to load workflow")
            
            # Update workflow with prompt and settings
            workflow = self._update_workflow_prompt(workflow, prompt, style, seed)
            
            # Submit to ComfyUI
            logger.info("Submitting workflow to ComfyUI...")
            prompt_id = self._queue_prompt(workflow)
            
            # Wait for completion and get result
            logger.info(f"Waiting for completion of prompt ID: {prompt_id}")
            image_path = self._wait_for_completion(prompt_id)
            
            logger.info(f"Image generated successfully: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            # Return placeholder path for now
            import hashlib
            placeholder_name = f"prompt_placeholder_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.png"
            return f"output/temp/{placeholder_name}"
    
    def _load_workflow(self):
        """Load the ComfyUI workflow from file"""
        try:
            logger.debug(f"Loading workflow from {self.workflow_path}")
            with open(self.workflow_path, 'r') as f:
                workflow = json.load(f)
            logger.debug(f"Workflow loaded successfully with {len(workflow)} nodes")
            return workflow
        except Exception as e:
            logger.error(f"Failed to load workflow: {e}")
            return None
    
    def _update_workflow_prompt(self, workflow, prompt, style, seed):
        """Update workflow with new prompt and settings"""
        # Enhanced quality and consistency prompts with weights
        quality_prefix = "score_9, score_8_up, score_7_up, (cel shading:1.3), (stylized features:1.2), (consistent character design:1.4), (detailed background:1.2), (professional comic art:1.3), "
        quality_suffix = ", (cartoon style:1.3), (high quality:1.4), (detailed illustration:1.2), (vibrant colors:1.1), (clean line art:1.2), (comic book panel:1.2)"
        
        # Build the complete prompt with weights
        styled_prompt = f"{quality_prefix}{prompt}{quality_suffix}"
        
        # Generate random seeds if not provided
        if seed == -1:
            main_seed = random.randint(1, 999999999999999)
            upscale_seed = random.randint(1, 999999999999999)
        else:
            main_seed = seed
            upscale_seed = seed + 1000 if seed > 0 else seed
        
        # Update positive prompt (node 6)
        if "6" in workflow:
            workflow["6"]["inputs"]["text"] = styled_prompt
            logger.debug(f"Updated positive prompt in node 6 with weighted elements")
        
        # Update seed in KSampler (node 31)
        if "31" in workflow:
            workflow["31"]["inputs"]["seed"] = main_seed
            logger.debug(f"Updated main seed to {main_seed} in node 31")
        
        # Update upscale seed (node 42) 
        if "42" in workflow:
            workflow["42"]["inputs"]["seed"] = upscale_seed
            logger.debug(f"Updated upscale seed to {upscale_seed} in node 42")
        
        return workflow
    
    def _queue_prompt(self, workflow):
        """Submit workflow to ComfyUI queue"""
        prompt_id = str(uuid.uuid4())
        
        data = {
            "prompt": workflow,
            "client_id": prompt_id
        }
        
        logger.debug(f"Submitting prompt to {self.base_url}/prompt")
        response = requests.post(f"{self.base_url}/prompt", json=data)
        
        if response.status_code != 200:
            logger.error(f"Queue prompt failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to queue prompt: {response.status_code} - {response.text}")
        
        result = response.json()
        actual_prompt_id = result.get("prompt_id", prompt_id)
        logger.info(f"Prompt queued successfully with ID: {actual_prompt_id}")
        return actual_prompt_id
    
    def _wait_for_completion(self, prompt_id, timeout=300):
        """Wait for image generation to complete"""
        start_time = time.time()
        logger.info(f"Waiting for completion of prompt {prompt_id}, timeout: {timeout}s")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/history/{prompt_id}")
                if response.status_code == 200:
                    history = response.json()
                    if prompt_id in history:
                        outputs = history[prompt_id].get("outputs", {})
                        logger.debug(f"Found outputs for {prompt_id}: {list(outputs.keys())}")
                        
                        for node_id, output in outputs.items():
                            if "images" in output:
                                images = output["images"]
                                if images:
                                    image_info = images[0]
                                    filename = image_info["filename"]
                                    image_path = f"comfyui_output/{filename}"
                                    logger.info(f"Image generation completed: {image_path}")
                                    return image_path
                
                logger.debug(f"Still waiting for {prompt_id}... ({int(time.time() - start_time)}s)")
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"Error checking completion: {e}")
                time.sleep(2)
        
        logger.error(f"Image generation timed out after {timeout}s")
        raise Exception("Image generation timed out")
