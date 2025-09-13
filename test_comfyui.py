#!/usr/bin/env python3
"""
ComfyUI Workflow Tester
Tests the comic_workflow.json file and ComfyUI connection
"""

import json
import requests
import sys
import os

def test_workflow_file():
    """Test if workflow file is valid JSON"""
    try:
        with open('workflows/comic_workflow_api.json', 'r') as f:
            workflow = json.load(f)
        
        print("✅ Workflow file loaded successfully")
        
        # Check for required nodes in API format
        required_types = ['CheckpointLoaderSimple', 'EmptyLatentImage', 'KSampler', 'VAEDecode', 'SaveImage', 'CLIPTextEncode']
        
        found_types = {}
        for node_id, node in workflow.items():
            if isinstance(node, dict) and "class_type" in node:
                node_type = node["class_type"]
                if node_type in required_types:
                    found_types[node_type] = found_types.get(node_type, 0) + 1
        
        for node_type in required_types:
            count = found_types.get(node_type, 0)
            if node_type == 'CLIPTextEncode':
                if count >= 2:  # Need positive and negative
                    print(f"✅ {node_type} nodes found ({count})")
                else:
                    print(f"❌ {node_type} needs at least 2 nodes, found {count}")
            elif count > 0:
                print(f"✅ {node_type} node found")
            else:
                print(f"❌ {node_type} node missing")
        
        return workflow
        
    except FileNotFoundError:
        print("❌ Workflow file not found: workflows/comic_workflow_api.json")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in workflow file: {e}")
        return None

def test_comfyui_connection():
    """Test connection to ComfyUI server"""
    try:
        response = requests.get("http://127.0.0.1:8000/system_stats", timeout=5)
        if response.status_code == 200:
            print("✅ ComfyUI server is running")
            return True
        else:
            print(f"❌ ComfyUI server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to ComfyUI server at 127.0.0.1:8000")
        print("   Make sure ComfyUI is running: python main.py --listen --port 8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ ComfyUI server connection timeout")
        return False

def test_workflow_submission():
    """Test submitting the workflow to ComfyUI"""
    workflow = test_workflow_file()
    if not workflow:
        return False
    
    if not test_comfyui_connection():
        return False
    
    # Update workflow with test prompt
    if workflow and "6" in workflow:
        workflow["6"]["inputs"]["text"] = "test comic panel, anime style, high quality"
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/prompt",
            json={
                "prompt": workflow,
                "client_id": "test_client"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Workflow submitted successfully")
            print(f"   Prompt ID: {result.get('prompt_id', 'unknown')}")
            return True
        else:
            print(f"❌ Failed to submit workflow: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error submitting workflow: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing ComfyUI Integration...")
    print("=" * 50)
    
    workflow_ok = test_workflow_file()
    print()
    
    connection_ok = test_comfyui_connection()
    print()
    
    if workflow_ok and connection_ok:
        submission_ok = test_workflow_submission()
        print()
        
        if submission_ok:
            print("🎉 All tests passed! ComfyUI integration is ready.")
        else:
            print("⚠️  Workflow file and connection OK, but submission failed.")
            print("   Check ComfyUI console for errors.")
    else:
        print("❌ Basic tests failed. Fix the issues above first.")
    
    print("\n📋 Next steps:")
    print("1. Start ComfyUI: python main.py --listen --port 8188")
    print("2. Download a model to ComfyUI/models/checkpoints/")
    print("3. Update workflow ckpt_name if needed")
    print("4. Test the Flask app comic generation")
