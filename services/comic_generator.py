from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)

class ComicGenerator:
    def __init__(self, ollama_service, comfyui_service):
        self.ollama = ollama_service
        self.comfyui = comfyui_service
        
    def create_comic(self, prompt: str, style: str, num_panels: int, layout_preset: str = 'Layout0', 
                    page: str = 'A4-P', geometry: Dict = None, show_prompts: bool = False) -> str:
        """Generate complete comic"""
        
        # Generate panel descriptions
        panels = self.ollama.generate_comic_panels(prompt, num_panels, style)
        
        # Generate images for each panel or create prompt placeholders
        panel_images = []
        for panel in panels:
            try:
                # Enhanced prompt with character and setting consistency
                enhanced_prompt = self._enhance_panel_prompt(panel, panels)
                
                image_path = self.comfyui.generate_image(
                    prompt=enhanced_prompt,
                    style=style,
                    seed=-1  # Use random seed for variety
                )
                panel_images.append(image_path)
            except Exception as e:
                logger.warning(f"ComfyUI unavailable for panel {panel['index']}: {e}")
                # Create a text placeholder with the prompt
                placeholder_path = self._create_prompt_placeholder(
                    enhanced_prompt if 'enhanced_prompt' in locals() else panel['description'], 
                    panel['index'], 
                    style
                )
                panel_images.append(placeholder_path)
        
        # Combine into comic layout
        comic_path = self._assemble_comic(panel_images, layout_preset, page, geometry)
        
        return comic_path
    
    def _enhance_panel_prompt(self, current_panel: Dict, all_panels: List[Dict]) -> str:
        """Enhance panel prompt with consistency elements and weights"""
        base_description = current_panel['description']
        
        # Extract character consistency from all panels
        character_refs = []
        for panel in all_panels:
            chars = panel.get('characters', '')
            if chars and chars not in character_refs:
                character_refs.append(chars)
        
        # Build consistency prompt elements
        consistency_elements = []
        if character_refs:
            main_character = character_refs[0] if character_refs else "main character"
            consistency_elements.append(f"(consistent character: {main_character}:1.3)")
        
        # Add setting consistency if available
        setting = current_panel.get('setting', '')
        if setting:
            consistency_elements.append(f"(setting: {setting}:1.1)")
        
        # Add camera angle emphasis
        camera_angle = current_panel.get('camera_angle', 'medium shot')
        consistency_elements.append(f"({camera_angle}:1.2)")
        
        # Add emotion/mood emphasis
        emotion = current_panel.get('emotion', 'neutral')
        consistency_elements.append(f"({emotion} mood:1.1)")
        
        # Combine everything
        consistency_prefix = ", ".join(consistency_elements)
        enhanced_prompt = f"{consistency_prefix}, {base_description}"
        
        logger.debug(f"Enhanced panel {current_panel['index']} prompt with consistency elements")
        return enhanced_prompt
    
    def _assemble_comic(self, image_paths: List[str], layout_preset: str, page: str, geometry: Dict = None) -> str:
        """Assemble panels into comic layout"""
        
        # Default layout if geometry not provided
        if not geometry:
            geometry = self._get_default_layout(layout_preset, page)
        
        # Calculate page dimensions based on page format
        page_width, page_height = self._get_page_dimensions(page)
        
        # Create canvas
        canvas = Image.new('RGB', (page_width, page_height), geometry.get('page', {}).get('bg', '#ffffff'))
        
        # Load and place images
        for i, img_path in enumerate(image_paths):
            if i >= len(geometry.get('cells', [])):
                break
                
            cell = geometry['cells'][i]
            
            # Calculate actual pixel positions
            margin = geometry.get('outerMarginPx', 24)
            content_width = page_width - (2 * margin)
            content_height = page_height - (2 * margin)
            
            x = margin + int(cell['x'] * content_width)
            y = margin + int(cell['y'] * content_height)
            w = int(cell['w'] * content_width)
            h = int(cell['h'] * content_height)
            
            # Load and resize image
            try:
                img = Image.open(img_path)
                img = img.resize((w, h), Image.LANCZOS)
                canvas.paste(img, (x, y))
            except Exception as e:
                logger.error(f"Failed to load panel image {img_path}: {e}")
                # Create placeholder
                placeholder = Image.new('RGB', (w, h), '#f0f0f0')
                draw = ImageDraw.Draw(placeholder)
                draw.text((w//2, h//2), f"Panel {i+1}", fill='black', anchor='mm')
                canvas.paste(placeholder, (x, y))
        
        # Save comic
        output_path = f"output/comics/comic_{os.urandom(8).hex()}.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        canvas.save(output_path)
        
        return output_path
    
    def _create_prompt_placeholder(self, prompt_text: str, panel_index: int, style: str) -> str:
        """Create a placeholder image showing the generated prompt"""
        try:
            from PIL import ImageFont
            
            # Create image dimensions
            img_width, img_height = 512, 768
            
            # Create image with style-based background
            bg_colors = {
                'anime': '#FFE4E1',     # light pink
                'manga': '#F0F8FF',     # light blue  
                'cartoon': '#F0FFF0',   # light green
                'realistic': '#FFF8DC'  # light beige
            }
            bg_color = bg_colors.get(style, '#F5F5F5')
            
            img = Image.new('RGB', (img_width, img_height), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fallback to default
            try:
                font_large = ImageFont.truetype("arial.ttf", 24)
                font_medium = ImageFont.truetype("arial.ttf", 18)
                font_small = ImageFont.truetype("arial.ttf", 14)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Draw panel number
            draw.text((20, 20), f"Panel {panel_index + 1}", fill='#333333', font=font_large)
            
            # Draw style indicator
            draw.text((20, 60), f"Style: {style.title()}", fill='#666666', font=font_medium)
            
            # Draw prompt text (wrapped)
            margin = 20
            max_width = img_width - (2 * margin)
            
            # Word wrap the prompt
            words = prompt_text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font_small)
                if bbox[2] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)  # Word is too long, add anyway
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw wrapped text
            y_pos = 120
            line_height = 20
            
            draw.text((margin, y_pos - 10), "Generated Prompt:", fill='#444444', font=font_medium)
            y_pos += 30
            
            for line in lines[:25]:  # Limit to 25 lines
                draw.text((margin, y_pos), line, fill='#222222', font=font_small)
                y_pos += line_height
                if y_pos > img_height - 50:
                    break
            
            # Add watermark
            draw.text((margin, img_height - 40), "ComfyUI Unavailable - Showing Generated Prompt", 
                     fill='#888888', font=font_small)
            
            # Save placeholder
            placeholder_path = f"output/temp/prompt_placeholder_{panel_index}_{os.urandom(4).hex()}.png"
            os.makedirs(os.path.dirname(placeholder_path), exist_ok=True)
            img.save(placeholder_path)
            
            return placeholder_path
            
        except Exception as e:
            logger.error(f"Failed to create prompt placeholder: {e}")
            # Fallback: create simple colored rectangle
            img = Image.new('RGB', (512, 768), '#F0F0F0')
            draw = ImageDraw.Draw(img)
            draw.text((50, 350), f"Panel {panel_index + 1}\nPrompt: {prompt_text[:100]}...", 
                     fill='black')
            
            placeholder_path = f"output/temp/simple_placeholder_{panel_index}.png"
            img.save(placeholder_path)
            return placeholder_path
    
    def _get_page_dimensions(self, page_format: str) -> Tuple[int, int]:
        """Get page dimensions in pixels (assuming 300 DPI)"""
        if page_format == 'A4-P':  # A4 Portrait
            return (2480, 3508)  # 210x297mm at 300 DPI
        elif page_format == 'A4-L':  # A4 Landscape
            return (3508, 2480)  # 297x210mm at 300 DPI
        else:
            return (2480, 3508)  # Default to A4 Portrait
    
    def _get_default_layout(self, layout_preset: str, page: str) -> Dict:
        """Get default layout geometry for preset"""
        # Simple 2x2 layout as default
        return {
            'cols': 2,
            'rows': 2,
            'gapPx': 20,
            'outerMarginPx': 60,
            'page': {'bg': '#ffffff'},
            'panel': {'bg': '#ffffff', 'borderPx': 2, 'borderColor': '#000000'},
            'cells': [
                {'index': 0, 'x': 0.0, 'y': 0.0, 'w': 0.48, 'h': 0.48},
                {'index': 1, 'x': 0.52, 'y': 0.0, 'w': 0.48, 'h': 0.48},
                {'index': 2, 'x': 0.0, 'y': 0.52, 'w': 0.48, 'h': 0.48},
                {'index': 3, 'x': 0.52, 'y': 0.52, 'w': 0.48, 'h': 0.48},
            ]
        }
