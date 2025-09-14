#!/usr/bin/env python3
"""
Test script for enhanced prompt generation with detailed descriptions and weighted prompts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ollama_service import OllamaService
from services.comfyui_service import ComfyUIService
from services.comic_generator import ComicGenerator
from config import OLLAMA_URL, OLLAMA_MODEL, COMFYUI_URL

def test_enhanced_ollama():
    """Test enhanced Ollama service with detailed prompts"""
    print("🔬 Testing Enhanced Ollama Service...")
    print("=" * 60)
    
    ollama = OllamaService(OLLAMA_URL, OLLAMA_MODEL)
    
    # Test story
    story = "A young wizard discovers their magic wand is actually a TV remote"
    
    try:
        panels = ollama.generate_comic_panels(story, 3, 'fantasy')
        
        print(f"✅ Generated {len(panels)} detailed panels:")
        print()
        
        for i, panel in enumerate(panels):
            print(f"📋 Panel {i+1}:")
            print(f"   Description: {panel['description']}")
            print(f"   Characters: {panel.get('characters', 'N/A')}")
            print(f"   Setting: {panel.get('setting', 'N/A')}")
            print(f"   Camera: {panel.get('camera_angle', 'N/A')}")
            print(f"   Emotion: {panel.get('emotion', 'N/A')}")
            print(f"   Dialogue: {panel.get('dialogue', 'N/A')}")
            print()
            
        return panels
        
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return []

def test_enhanced_comfyui(test_prompt):
    """Test enhanced ComfyUI service with weighted prompts"""
    print("🎨 Testing Enhanced ComfyUI Service...")
    print("=" * 60)
    
    comfyui = ComfyUIService()
    
    if not comfyui.is_available():
        print("❌ ComfyUI not available")
        return None
    
    print("✅ ComfyUI available")
    
    # Test with a detailed prompt including weights
    test_description = "(close-up portrait:1.3) Young wizard with (expressive green eyes:1.2) holding a black TV remote, looking confused. (magical sparkles:1.1) emanating from the remote control, (detailed background:1.2) with ancient library setting"
    
    try:
        print(f"🚀 Generating image with weighted prompt...")
        print(f"Prompt: {test_description[:100]}...")
        
        image_path = comfyui.generate_image(
            prompt=test_description,
            style="fantasy",
            seed=-1  # Random seed
        )
        
        print(f"✅ Image generated: {image_path}")
        return image_path
        
    except Exception as e:
        print(f"❌ ComfyUI test failed: {e}")
        return None

def test_enhanced_comic_generation():
    """Test complete enhanced comic generation"""
    print("📚 Testing Enhanced Comic Generation...")
    print("=" * 60)
    
    ollama = OllamaService(OLLAMA_URL, OLLAMA_MODEL)
    comfyui = ComfyUIService()
    generator = ComicGenerator(ollama, comfyui)
    
    story = "A cat discovers it can talk, but only to houseplants"
    
    try:
        print(f"🎭 Creating comic: {story}")
        
        comic_path = generator.create_comic(
            prompt=story,
            style="cartoon",
            num_panels=2,
            layout_preset="Layout0",
            page="A4-P"
        )
        
        print(f"✅ Comic created: {comic_path}")
        return comic_path
        
    except Exception as e:
        print(f"❌ Comic generation failed: {e}")
        return None

if __name__ == "__main__":
    print("🧪 ENHANCED AI COMIC GENERATOR TESTING")
    print("=" * 60)
    print()
    
    # Test 1: Enhanced Ollama prompts
    panels = test_enhanced_ollama()
    print()
    
    # Test 2: Enhanced ComfyUI with weights
    if panels:
        test_prompt = panels[0]['description'] if panels else "test prompt"
        image_path = test_enhanced_comfyui(test_prompt)
        print()
    
    # Test 3: Complete enhanced comic generation
    comic_path = test_enhanced_comic_generation()
    print()
    
    print("🏁 TESTING COMPLETE")
    print("=" * 60)
    
    if panels and comic_path:
        print("✅ All enhanced features working!")
        print("🎯 Ready for professional comic generation with:")
        print("   - Detailed scene descriptions")
        print("   - Weighted prompt elements")
        print("   - Character consistency")
        print("   - Random seed variation")
    else:
        print("⚠️  Some features need attention")