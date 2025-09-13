# ComfyUI Setup Guide for AI Comic Generator

## Prerequisites

1. **Python 3.8+** installed
2. **Git** installed
3. **CUDA-compatible GPU** (recommended for fast generation)

## Installation Steps

### 1. Clone ComfyUI
```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
```

### 2. Install Dependencies
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### 3. Download Base Model
You need at least one model. Download one of these to `ComfyUI/models/checkpoints/`:

**SDXL Base (Recommended for comics):**
- Download: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
- Place in: `ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors`

**Alternative - SD 1.5 (Lighter):**
- Download: https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors
- Place in: `ComfyUI/models/checkpoints/v1-5-pruned-emaonly.safetensors`

### 4. Start ComfyUI Server
```bash
python main.py --listen --port 8188
```

You should see:
```
Starting server
To see the GUI go to: http://127.0.0.1:8188
```

## Workflow Integration

The AI Comic Generator uses the workflow file: `workflows/comic_workflow.json`

### Key Workflow Nodes:

1. **Node 1**: `CheckpointLoaderSimple` - Loads the AI model
2. **Node 2**: `EmptyLatentImage` - Sets image dimensions (512x768 for comic panels)
3. **Node 3**: `KSampler` - Generates the image (seed, steps, cfg)
4. **Node 4**: `VAEDecode` - Converts latent to image
5. **Node 5**: `SaveImage` - Saves the final image
6. **Node 6**: `CLIPTextEncode` - **PROMPT INPUT** (this is where your text goes)
7. **Node 7**: `CLIPTextEncode` - Negative prompt (what to avoid)

### How the Integration Works:

1. **Prompt Input**: Your comic panel description goes into Node 6
2. **Style Addition**: Automatically adds ", [style] style, high quality, detailed, comic panel art"
3. **Seed Control**: Node 3 seed gets set for consistency
4. **Image Output**: Node 5 saves the image, which gets downloaded by the Flask app

### Customizing the Workflow:

**To change the model used:**
- Edit Node 1's `ckpt_name` to match your model filename

**To adjust image quality:**
- Node 3: Increase `steps` (20-30 for better quality)
- Node 3: Adjust `cfg` (7-12 for stronger prompt following)

**To change image size:**
- Node 2: Modify `width` and `height`

**To improve prompts:**
- Node 6: The Flask app will populate this automatically
- Node 7: Edit negative prompt to exclude unwanted elements

## Testing Connection

1. Start ComfyUI: `python main.py --listen --port 8188`
2. Start the Flask app: `python app.py`
3. Check the status indicators in the web interface
4. ComfyUI should show a green ball when connected

## Troubleshooting

**"ComfyUI offline" in status:**
- Check ComfyUI is running on port 8188
- Verify no firewall blocking the connection
- Check ComfyUI console for errors

**"Workflow file not found":**
- Ensure `workflows/comic_workflow.json` exists
- Check the path in `config.py` (COMFYUI_WORKFLOW)

**"Model not found" error:**
- Download a model to `ComfyUI/models/checkpoints/`
- Update the workflow's `ckpt_name` to match your model

**Slow generation:**
- Check GPU is being used (ComfyUI console shows device)
- Reduce image dimensions in Node 2
- Reduce steps in Node 3

**Out of memory:**
- Use a smaller model (SD 1.5 instead of SDXL)
- Reduce batch_size in Node 2 to 1
- Lower image resolution

## Expected Output

When working correctly:
1. You enter a comic prompt in the web interface
2. Ollama generates detailed panel descriptions
3. Each panel description gets sent to ComfyUI
4. ComfyUI generates comic-style images
5. Images are assembled into a final comic layout

The workflow is designed for:
- **Style**: Comic panel art
- **Aspect**: Portrait (512x768) for vertical comic panels
- **Quality**: High detail with clean lines
- **Speed**: ~10-30 seconds per panel depending on hardware

## Model Recommendations

**For Anime/Manga style:**
- AnythingV3, AnythingV5
- CounterfeitV3
- AbyssOrangeMix

**For Western Comics:**
- DreamShaper
- Realistic Vision
- epiCRealism

**For Cartoon style:**
- Disney Pixar models
- Toon You
- 3D Animation Diffusion
