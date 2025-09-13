// Status checking functionality
let statusCheckInterval;

function updateStatusIndicator(serviceId, status) {
    const indicator = document.querySelector(`#${serviceId}Status .status-ball`);
    if (indicator) {
        indicator.className = `status-ball ${status}`;
    }
}

async function checkServiceStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        updateStatusIndicator('ollama', data.ollama);
        updateStatusIndicator('comfyui', data.comfyui);
        
    } catch (error) {
        console.error('Failed to check service status:', error);
        updateStatusIndicator('ollama', 'offline');
        updateStatusIndicator('comfyui', 'offline');
    }
}

function startStatusChecking() {
    // Check immediately
    checkServiceStatus();
    
    // Then check every 10 seconds
    statusCheckInterval = setInterval(checkServiceStatus, 10000);
}

function stopStatusChecking() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
}

// Layout presets adapted from AI Comic Factory
const LAYOUT_PRESETS = {
    Layout0: {
        id: "Layout0",
        label: "2×2 grid (4 equal)",
        cols: 2,
        rows: 2,
        panels: [
            { colStart: 1, colSpan: 1, rowStart: 1, rowSpan: 1 },
            { colStart: 2, colSpan: 1, rowStart: 1, rowSpan: 1 },
            { colStart: 1, colSpan: 1, rowStart: 2, rowSpan: 1 },
            { colStart: 2, colSpan: 1, rowStart: 2, rowSpan: 1 },
        ]
    },
    Layout1: {
        id: "Layout1",
        label: "Tall middle columns",
        cols: 2,
        rows: 3,
        panels: [
            { colStart: 1, colSpan: 1, rowStart: 1, rowSpan: 1 },
            { colStart: 2, colSpan: 1, rowStart: 1, rowSpan: 2 },
            { colStart: 1, colSpan: 1, rowStart: 2, rowSpan: 2 },
            { colStart: 2, colSpan: 1, rowStart: 3, rowSpan: 1 },
        ]
    },
    Layout2: {
        id: "Layout2",
        label: "Right column tall",
        cols: 3,
        rows: 2,
        panels: [
            { colStart: 1, colSpan: 1, rowStart: 1, rowSpan: 1 },
            { colStart: 2, colSpan: 1, rowStart: 1, rowSpan: 1 },
            { colStart: 3, colSpan: 1, rowStart: 1, rowSpan: 2 },
            { colStart: 1, colSpan: 2, rowStart: 2, rowSpan: 1 },
        ]
    },
    Layout3: {
        id: "Layout3",
        label: "Wide top + mixed right",
        cols: 3,
        rows: 2,
        panels: [
            { colStart: 1, colSpan: 2, rowStart: 1, rowSpan: 1 },
            { colStart: 3, colSpan: 1, rowStart: 1, rowSpan: 1 },
            { colStart: 1, colSpan: 1, rowStart: 2, rowSpan: 1 },
            { colStart: 2, colSpan: 2, rowStart: 2, rowSpan: 1 },
        ]
    },
    Layout5: {
        id: "Layout5",
        label: "Stacked big bottom (5 panels)",
        cols: 3,
        rows: 3,
        panels: [
            { colStart: 1, colSpan: 2, rowStart: 1, rowSpan: 1 },
            { colStart: 3, colSpan: 1, rowStart: 1, rowSpan: 1 },
            { colStart: 1, colSpan: 1, rowStart: 2, rowSpan: 1 },
            { colStart: 2, colSpan: 2, rowStart: 2, rowSpan: 1 },
            { colStart: 1, colSpan: 3, rowStart: 3, rowSpan: 1 },
        ]
    }
};

function renderLayoutPreview() {
    const pageFormat = document.getElementById('pageFormat').value;
    const layoutId = document.getElementById('layout').value;
    const margin = parseInt(document.getElementById('margin').value);
    const gutter = parseInt(document.getElementById('gutter').value);
    const showOutlines = document.getElementById('showOutlines').checked;
    
    const preset = LAYOUT_PRESETS[layoutId];
    if (!preset) return;
    
    const isPortrait = pageFormat === 'a4p';
    const orientationClass = isPortrait ? 'portrait' : 'landscape';
    
    // Create the A4 page container
    const previewHtml = `
        <div class="a4-page ${orientationClass}">
            <div class="a4-content" style="padding: ${margin}px;">
                <div class="layout-grid ${showOutlines ? 'debug' : ''}" 
                     style="grid-template-columns: repeat(${preset.cols}, minmax(0, 1fr)); 
                            grid-template-rows: repeat(${preset.rows}, minmax(0, 1fr)); 
                            gap: ${gutter}px;">
                    ${preset.panels.map((panel, i) => `
                        <div style="grid-column: ${panel.colStart} / span ${panel.colSpan}; 
                                    grid-row: ${panel.rowStart} / span ${panel.rowSpan};">
                            <div class="panel-box">
                                <span>#${i + 1}</span>
                                <div class="panel-index">${panel.colSpan}×${panel.rowSpan}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('layoutPreview').innerHTML = previewHtml;
}

// Update preview when any control changes
function setupLayoutPreview() {
    const controls = ['pageFormat', 'layout', 'margin', 'gutter', 'showOutlines'];
    controls.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', renderLayoutPreview);
            element.addEventListener('input', renderLayoutPreview);
        }
    });
    
    // Initial render
    renderLayoutPreview();
}

let currentComicUrl = null;

async function generateComic() {
    const prompt = document.getElementById('prompt').value;
    const style = document.getElementById('style').value;
    const layoutId = document.getElementById('layout').value;
    const pageFormat = document.getElementById('pageFormat').value;
    const margin = parseInt(document.getElementById('margin').value);
    const gutter = parseInt(document.getElementById('gutter').value);
    
    if (!prompt) {
        alert('Please enter a comic description');
        return;
    }
    
    const preset = LAYOUT_PRESETS[layoutId];
    const num_panels = preset.panels.length;
    
    // Show progress
    document.getElementById('progress').classList.remove('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('preview').classList.add('hidden');
    document.getElementById('generateBtn').disabled = true;
    
    try {
        // Step 1: Generate story panels
        updateStatus('Generating story panels...');
        const storyResponse = await fetch('/api/generate_story', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({prompt, style, num_panels})
        });
        
        const storyData = await storyResponse.json();
        
        if (storyData.success) {
            displayPanelDescriptions(storyData.panels);
            
            // Step 2: Generate complete comic
            updateStatus('Creating comic images...');
            
            // Create geometry data for backend
            const geometry = {
                cols: preset.cols,
                rows: preset.rows,
                gapPx: gutter,
                outerMarginPx: margin,
                page: { bg: '#ffffff', borderPx: 1, borderColor: '#e5e7eb' },
                panel: { bg: '#ffffff', borderPx: 1, borderColor: '#d1d5db', radiusPx: 4 },
                cells: preset.panels.map((panel, i) => {
                    // Calculate fractional positions for backend
                    const totalCols = preset.cols;
                    const totalRows = preset.rows;
                    const colGaps = totalCols - 1;
                    const rowGaps = totalRows - 1;
                    
                    const cellWidth = (1 - (colGaps * gutter) / 1000) / totalCols;
                    const cellHeight = (1 - (rowGaps * gutter) / 1000) / totalRows;
                    
                    const x = (panel.colStart - 1) * cellWidth + ((panel.colStart - 1) * gutter) / 1000;
                    const y = (panel.rowStart - 1) * cellHeight + ((panel.rowStart - 1) * gutter) / 1000;
                    const w = panel.colSpan * cellWidth + ((panel.colSpan - 1) * gutter) / 1000;
                    const h = panel.rowSpan * cellHeight + ((panel.rowSpan - 1) * gutter) / 1000;
                    
                    return { index: i, x, y, w, h };
                })
            };
            
            const comicResponse = await fetch('/api/generate_comic', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    prompt, 
                    style, 
                    num_panels,
                    layout_preset: layoutId,
                    page: pageFormat,
                    geometry
                })
            });
            
            const comicData = await comicResponse.json();
            
            if (comicData.success) {
                displayComic(comicData.comic_url);
                updateStatus('Comic generated successfully!');
            } else {
                throw new Error(comicData.error || 'Comic generation failed');
            }
        } else {
            throw new Error(storyData.error || 'Story generation failed');
        }
        
    } catch (error) {
        console.error('Generation failed:', error);
        updateStatus('Generation failed: ' + error.message);
        alert('Failed to generate comic: ' + error.message);
    } finally {
        document.getElementById('generateBtn').disabled = false;
        setTimeout(() => {
            document.getElementById('progress').classList.add('hidden');
        }, 2000);
    }
}

function updateStatus(message) {
    document.getElementById('status').textContent = message;
}

function displayPanelDescriptions(panels) {
    const preview = document.getElementById('preview');
    const panelList = document.getElementById('panelList');
    
    panelList.innerHTML = '';
    panels.forEach((panel, index) => {
        // Create the ComfyUI prompt (style + description)
        const style = document.getElementById('style').value;
        const comfyuiPrompt = `${panel.description}, ${style} style, high quality, detailed`;
        
        const panelDiv = document.createElement('div');
        panelDiv.className = 'panel-description';
        panelDiv.innerHTML = `
            <h3>Panel ${index + 1}</h3>
            <p><strong>Scene:</strong> ${panel.description}</p>
            ${panel.dialogue ? `<p><strong>Dialogue:</strong> "${panel.dialogue}"</p>` : ''}
            <p><em>Camera: ${panel.camera_angle} | Emotion: ${panel.emotion}</em></p>
            <div class="comfyui-prompt">
                <strong>ComfyUI Prompt:</strong>
                <div class="prompt-text">${comfyuiPrompt}</div>
            </div>
        `;
        panelList.appendChild(panelDiv);
    });
    
    preview.classList.remove('hidden');
}

function displayComic(url) {
    currentComicUrl = url;
    document.getElementById('comicImage').src = url;
    document.getElementById('result').classList.remove('hidden');
}

function downloadComic() {
    if (currentComicUrl) {
        const a = document.createElement('a');
        a.href = currentComicUrl;
        a.download = `comic_${Date.now()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}

// Add some example prompts for testing
function loadExamplePrompt(example) {
    const examples = {
        1: "A robot chef discovers emotions while cooking for the last human on Earth",
        2: "Two cats argue about who owns the cardboard box while a dog watches confused",
        3: "A time traveler keeps trying to fix their broken coffee machine but keeps going to the wrong century"
    };
    
    document.getElementById('prompt').value = examples[example] || "";
}

// Add example buttons on page load
window.addEventListener('DOMContentLoaded', function() {
    // Setup layout preview
    setupLayoutPreview();
    
    // Start status checking
    startStatusChecking();
    
    const inputSection = document.querySelector('.input-section');
    const examplesDiv = document.createElement('div');
    examplesDiv.innerHTML = `
        <div style="margin: 10px 0; text-align: center;">
            <small style="color: #666;">Quick examples:</small><br>
            <button type="button" onclick="loadExamplePrompt(1)" style="margin: 5px; padding: 5px 10px; font-size: 12px;">Robot Chef</button>
            <button type="button" onclick="loadExamplePrompt(2)" style="margin: 5px; padding: 5px 10px; font-size: 12px;">Cat Drama</button>
            <button type="button" onclick="loadExamplePrompt(3)" style="margin: 5px; padding: 5px 10px; font-size: 12px;">Time Travel</button>
        </div>
    `;
    inputSection.appendChild(examplesDiv);
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    stopStatusChecking();
});
