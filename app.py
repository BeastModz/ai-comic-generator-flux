from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import logging
import os
import requests
from datetime import datetime
from services.ollama_service import OllamaService
from services.comfyui_service import ComfyUIService
from services.comic_generator import ComicGenerator
import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config.from_object(config)

# Initialize services
ollama = OllamaService(config.OLLAMA_URL, config.OLLAMA_MODEL)
comfyui = ComfyUIService(config.COMFYUI_URL)
comic_gen = ComicGenerator(ollama, comfyui)

@app.route('/')
def index():
    """Render the main UI"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Check status of Ollama and ComfyUI services"""
    try:
        # Check Ollama
        ollama_status = "checking"
        try:
            ollama_response = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=3)
            ollama_status = "online" if ollama_response.status_code == 200 else "offline"
        except:
            ollama_status = "offline"
        
        # Check ComfyUI
        comfyui_status = "checking"
        try:
            comfyui_response = requests.get(f"{config.COMFYUI_URL}/system_stats", timeout=3)
            comfyui_status = "online" if comfyui_response.status_code == 200 else "offline"
        except:
            comfyui_status = "offline"
        
        return jsonify({
            'ollama': ollama_status,
            'comfyui': comfyui_status
        })
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return jsonify({
            'ollama': 'offline',
            'comfyui': 'offline'
        }), 500

@app.route('/api/generate_story', methods=['POST'])
def generate_story():
    """Expand user prompt into comic panels"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        style = data.get('style', 'anime')
        num_panels = data.get('num_panels', 4)
        
        logger.info(f"Generating story for prompt: {prompt[:100]}...")
        
        # Use Ollama to expand the prompt into panel descriptions
        panels = ollama.generate_comic_panels(prompt, num_panels, style)
        
        return jsonify({
            'success': True,
            'panels': panels,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Story generation failed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate_panel', methods=['POST'])
def generate_panel():
    """Generate a single comic panel image"""
    try:
        data = request.json
        panel_description = data.get('description', '')
        style = data.get('style', 'anime')
        panel_index = data.get('panel_index', 0)
        
        logger.info(f"Generating panel {panel_index}: {panel_description[:100]}...")
        
        # Generate image using ComfyUI
        image_path = comfyui.generate_image(
            prompt=panel_description,
            style=style,
            seed=panel_index  # Use panel index as seed for consistency
        )
        
        return send_file(image_path, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Panel generation failed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate_comic', methods=['POST'])
def generate_comic():
    """Generate complete comic from prompt"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        style = data.get('style', 'anime')
        num_panels = data.get('num_panels', 4)
        layout_preset = data.get('layout_preset', 'Layout0')
        page = data.get('page', 'A4-P')
        geometry = data.get('geometry', {})
        
        logger.info(f"Generating complete comic: {prompt[:100]}...")
        
        # Generate the complete comic
        comic_path = comic_gen.create_comic(
            prompt=prompt,
            style=style,
            num_panels=num_panels,
            layout_preset=layout_preset,
            page=page,
            geometry=geometry,
            show_prompts=True  # Show prompts when ComfyUI unavailable
        )
        
        return jsonify({
            'success': True,
            'comic_url': f'/comics/{os.path.basename(comic_path)}',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Comic generation failed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/comics/<filename>')
def serve_comic(filename):
    """Serve generated comic images"""
    return send_file(os.path.join(config.OUTPUT_DIR, filename))

if __name__ == '__main__':
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    app.run(debug=True, port=5000)
