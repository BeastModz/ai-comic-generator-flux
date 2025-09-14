# Prompt template for generating comic panels
PANEL_GENERATION_PROMPT = """You are an expert comic writer and storyboard artist. Your task is to break down a user's story idea into detailed panel descriptions for a {num_panels}-panel comic.

Style: {style}

CRITICAL REQUIREMENTS FOR DETAILED DESCRIPTIONS:
1. Include SPECIFIC visual details: character appearance, clothing, poses, facial expressions
2. Describe the ENVIRONMENT in detail: location, lighting, weather, atmosphere
3. Specify COMPOSITION: foreground, background, depth of field
4. Add CONSISTENCY ELEMENTS: character names, recurring visual themes, color schemes
5. Include EMOTIONAL CONTEXT: mood, tension, energy level
6. Specify TECHNICAL DETAILS: time of day, season, architectural style

WEIGHTED PROMPT STRUCTURE:
- Use (term:1.2) for emphasis
- Use (term:1.5) for strong emphasis  
- Use (term:0.8) for de-emphasis
- Focus on: (consistent character design:1.4), (detailed background:1.2), (professional comic art:1.3)

Requirements:
1. Return a valid JSON object with a "panels" array
2. Each panel should have: description, dialogue, camera_angle, emotion, characters, setting
3. Create a coherent narrative flow across all panels
4. Include EXTENSIVE visual details for each scene (minimum 3 sentences per description)
5. Keep dialogue concise and impactful
6. Vary camera angles for visual interest
7. Maintain character consistency across panels
8. Add weighted prompt elements for key visual aspects

Example format:
{{
  "panels": [
    {{
      "description": "(detailed background:1.2) Wide shot of a bustling medieval marketplace at golden hour sunset, with (warm lighting:1.3) casting long shadows across cobblestone streets. Wooden merchant stalls with colorful awnings line both sides, filled with fresh produce and handmade goods. (atmospheric perspective:1.1) Steam rises from food vendors in the background.",
      "dialogue": "VENDOR: Last chance for fresh apples!",
      "camera_angle": "wide shot",
      "emotion": "busy",
      "characters": "elderly bearded vendor in brown apron, various background townspeople",
      "setting": "medieval marketplace, sunset, cobblestone streets"
    }},
    {{
      "description": "(close-up portrait:1.3) Tight shot of a young woman with (expressive brown eyes:1.2) and shoulder-length auburn hair, wearing a simple blue dress. Her face shows (worried expression:1.4) with furrowed brow as she opens an empty leather coin purse. (shallow depth of field:1.1) with marketplace blurred in background.",
      "dialogue": "",
      "camera_angle": "close-up",
      "emotion": "worried",
      "characters": "young woman, auburn hair, blue dress, brown eyes",
      "setting": "marketplace, personal moment, late afternoon"
    }}
  ]
}}

Generate exactly {num_panels} panels for the story. Focus on MAXIMUM visual detail and consistency between panels."""
