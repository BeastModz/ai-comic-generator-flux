#!/usr/bin/env python3
"""
Test ComfyUI service directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.comfyui_service import ComfyUIService
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def test_comfyui():
    print("Testing ComfyUI service...")
    
    # Initialize service
    comfyui = ComfyUIService()
    
    # Test availability
    print(f"ComfyUI available: {comfyui.is_available()}")
    
    # Test status
    status = comfyui.get_status()
    print(f"Status: {status}")
    
    # Test workflow loading
    workflow = comfyui._load_workflow()
    if workflow:
        print(f"Workflow loaded successfully: {len(workflow)} nodes")
        print("Workflow nodes:", list(workflow.keys()))
    else:
        print("Failed to load workflow")
        return
    
    # Test prompt update
    test_prompt = "a cute cat superhero"
    updated_workflow = comfyui._update_workflow_prompt(workflow, test_prompt, "comic", 12345)
    print(f"Workflow updated with prompt: {test_prompt}")
    
    # Test actual image generation
    try:
        print("Attempting to generate test image...")
        image_path = comfyui.generate_image(test_prompt, "comic", 12345)
        print(f"SUCCESS: Image generated at {image_path}")
    except Exception as e:
        print(f"ERROR: Image generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comfyui()
