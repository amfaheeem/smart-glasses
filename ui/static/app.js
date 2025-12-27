// WebSocket connection
let ws = null;
let currentFrame = null;
let latestTracks = {};
let totalFrames = 0;

// Canvas
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// Status
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const frameInfo = document.getElementById('frame-info');

// Controls
const btnPlay = document.getElementById('btn-play');
const btnPause = document.getElementById('btn-pause');
const speedSelect = document.getElementById('speed-select');

// Thresholds
const detectionConfSlider = document.getElementById('detection-conf');
const detectionConfValue = document.getElementById('detection-conf-value');
const trackerIouSlider = document.getElementById('tracker-iou');
const trackerIouValue = document.getElementById('tracker-iou-value');
const fusionCooldownSlider = document.getElementById('fusion-cooldown');
const fusionCooldownValue = document.getElementById('fusion-cooldown-value');

// Event feed
const eventFeed = document.getElementById('event-feed');

// Initialize
function init() {
    connectWebSocket();
    setupEventListeners();
}

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        statusIndicator.classList.add('connected');
        statusText.textContent = 'Connected';
    };
    
    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        
        if (msg.type === 'frame') {
            handleFrame(msg);
        } else if (msg.type === 'event') {
            handleEvent(msg);
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        statusIndicator.classList.remove('connected');
        statusIndicator.classList.add('error');
        statusText.textContent = 'Error';
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        statusIndicator.classList.remove('connected');
        statusText.textContent = 'Disconnected';
        
        // Attempt to reconnect after 2 seconds
        setTimeout(connectWebSocket, 2000);
    };
}

function setupEventListeners() {
    // Play/pause
    btnPlay.addEventListener('click', () => {
        sendControl('play', null);
    });
    
    btnPause.addEventListener('click', () => {
        sendControl('pause', null);
    });
    
    // Speed
    speedSelect.addEventListener('change', (e) => {
        const speed = parseFloat(e.target.value);
        sendControl('speed', { speed });
    });
    
    // Thresholds
    detectionConfSlider.addEventListener('input', (e) => {
        const value = parseInt(e.target.value) / 100;
        detectionConfValue.textContent = value.toFixed(2);
    });
    
    detectionConfSlider.addEventListener('change', (e) => {
        const value = parseInt(e.target.value) / 100;
        sendControl('set_threshold', { detection_conf_threshold: value });
    });
    
    trackerIouSlider.addEventListener('input', (e) => {
        const value = parseInt(e.target.value) / 100;
        trackerIouValue.textContent = value.toFixed(2);
    });
    
    trackerIouSlider.addEventListener('change', (e) => {
        const value = parseInt(e.target.value) / 100;
        sendControl('set_threshold', { tracker_iou_threshold: value });
    });
    
    fusionCooldownSlider.addEventListener('input', (e) => {
        const value = parseInt(e.target.value) / 10;
        fusionCooldownValue.textContent = value.toFixed(1) + 's';
    });
    
    fusionCooldownSlider.addEventListener('change', (e) => {
        const value = parseInt(e.target.value) / 10;
        sendControl('set_threshold', { fusion_cooldown_seconds: value });
    });
}

function sendControl(kind, value) {
    fetch('/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ kind, value })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status !== 'ok') {
            console.error('Control error:', data);
        }
    })
    .catch(error => console.error('Control request failed:', error));
}

function handleFrame(msg) {
    currentFrame = msg;
    
    // Update frame info
    frameInfo.textContent = `Frame: ${msg.frame_id}`;
    
    // Draw frame
    const img = new Image();
    img.onload = () => {
        canvas.width = msg.width;
        canvas.height = msg.height;
        ctx.drawImage(img, 0, 0);
        
        // Draw overlays
        drawOverlays(msg.frame_id);
    };
    img.src = 'data:image/jpeg;base64,' + msg.jpg_base64;
}

function drawOverlays(frameId) {
    // Draw tracks for this frame
    const tracks = latestTracks[frameId] || [];
    
    tracks.forEach(track => {
        const [x, y, w, h] = track.bbox;
        
        // Convert normalized to pixel coordinates
        const px = x * canvas.width;
        const py = y * canvas.height;
        const pw = w * canvas.width;
        const ph = h * canvas.height;
        
        // Determine color based on stability
        const color = track.stable ? '#4CAF50' : '#FFC107';
        
        // Draw bounding box
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(px, py, pw, ph);
        
        // Draw label
        const label = `${track.label} #${track.track_id}`;
        ctx.fillStyle = color;
        ctx.font = '14px Arial';
        
        // Background for text
        const textMetrics = ctx.measureText(label);
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(px, py - 20, textMetrics.width + 8, 20);
        
        // Text
        ctx.fillStyle = color;
        ctx.fillText(label, px + 4, py - 6);
    });
}

function handleEvent(msg) {
    const { event_type, data } = msg;
    
    // Store tracks for overlay
    if (event_type === 'TrackUpdate') {
        if (!latestTracks[data.frame_id]) {
            latestTracks[data.frame_id] = [];
        }
        latestTracks[data.frame_id].push(data);
        
        // Keep only recent frames to avoid memory leak
        const frameIds = Object.keys(latestTracks).map(Number);
        if (frameIds.length > 100) {
            const oldestFrame = Math.min(...frameIds);
            delete latestTracks[oldestFrame];
        }
    }
    
    // Add to event feed
    addEventToFeed(event_type, data);
}

function addEventToFeed(eventType, data) {
    const eventItem = document.createElement('div');
    eventItem.className = 'event-item';
    
    const timestamp = formatTimestamp(data.timestamp_ms);
    const timeSpan = `<span class="event-time">[${timestamp}]</span>`;
    
    if (eventType === 'DetectionResult') {
        eventItem.classList.add('detection');
        eventItem.innerHTML = `${timeSpan} <strong>Detection:</strong> ${data.objects.length} object(s) in frame ${data.frame_id}`;
    }
    else if (eventType === 'TrackUpdate') {
        eventItem.classList.add('track');
        eventItem.innerHTML = `${timeSpan} <strong>Track #${data.track_id}:</strong> ${data.label} ${data.stable ? '(stable)' : ''}`;
    }
    else if (eventType === 'NavigationGuidance') {
        eventItem.classList.add('navigation');
        const urgencyClass = `urgency-${data.urgency}`;
        eventItem.innerHTML = `${timeSpan} <strong>Navigation:</strong> ${data.guidance_text} <span class="event-urgency ${urgencyClass}">${data.urgency.toUpperCase()}</span>`;
    }
    else if (eventType === 'FusionAnnouncement') {
        eventItem.classList.add('announcement');
        eventItem.innerHTML = `${timeSpan} <strong>📢 Announcement:</strong> ${data.text} <em>(${data.kind})</em>`;
    }
    else if (eventType === 'SystemMetric') {
        // Don't show metrics in feed (too noisy)
        return;
    }
    
    // Add to feed
    eventFeed.insertBefore(eventItem, eventFeed.firstChild);
    
    // Limit feed size
    while (eventFeed.children.length > 100) {
        eventFeed.removeChild(eventFeed.lastChild);
    }
}

function formatTimestamp(ms) {
    const date = new Date(ms);
    return date.toLocaleTimeString('en-US', { hour12: false });
}

// Start
init();

