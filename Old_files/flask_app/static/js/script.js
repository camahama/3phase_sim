const canvas = document.getElementById('simulationCanvas');
const ctx = canvas.getContext('2d');

// Constants from Python (adjust as needed for frontend)
const VOLTAGE_RMS = 230.0;
const BASE_PIXELS_PER_AMP = 10.0; // By AI agent Mima 2026-02-05 18:40:00
const PHASOR_SCALE = 5; // Adjust this for better visibility of phasors # By AI agent Mima 2026-02-05 18:40:00
const SINE_WAVE_HEIGHT_SCALE = 10; // Adjust this for better visibility of sine waves # By AI agent Mima 2026-02-05 18:40:00

// Colors - matching Python backend as closely as possible
const COLOR_L1 = '#FF3232'; // Red
const COLOR_L2 = '#32C832'; // Green
const COLOR_L3 = '#3264FF'; // Blue
const COLOR_N = '#FFFFFF';  // White
const COLOR_P12_LABEL = '#FFFF00'; // Yellow
const COLOR_P23_LABEL = '#FF00FF'; // Magenta
const COLOR_P31_LABEL = '#FFA500'; // Orange

const COLOR_AXIS = '#787878'; // Darker gray for axes # By AI agent Mima 2026-02-05 18:40:00

let animationFrameId = null; // To control animation loop # By AI agent Mima 2026-02-05 18:40:00
let isPaused = false; // By AI agent Mima 2026-02-05 18:40:00
let simulationTime = 0; // By AI agent Mima 2026-02-05 18:40:00
let lastUpdateTime = performance.now(); // By AI agent Mima 2026-02-05 18:40:00
const INITIAL_FREQ = 0.02; // By AI agent Mima 2026-02-05 18:40:00
const MAX_FREQ = 0.5; // Adjusted for web visualization # By AI agent Mima 2026-02-05 18:40:00
let currentFreq = INITIAL_FREQ; // By AI agent Mima 2026-02-05 18:40:00

// DOM elements
const pDeltaSliders = [
    document.getElementById('p_delta_1'),
    document.getElementById('p_delta_2'),
    document.getElementById('p_delta_3')
];
const pDeltaValues = [
    document.getElementById('p_delta_1_val'),
    document.getElementById('p_delta_2_val'),
    document.getElementById('p_delta_3_val')
];

const pYSliders = [
    document.getElementById('p_y_1'),
    document.getElementById('p_y_2'),
    document.getElementById('p_y_3')
];
const pYValues = [
    document.getElementById('p_y_1_val'),
    document.getElementById('p_y_2_val'),
    document.getElementById('p_y_3_val')
];

const iL1Mag = document.getElementById('i_l1_mag');
const iL1Angle = document.getElementById('i_l1_angle');
const iL2Mag = document.getElementById('i_l2_mag');
const iL2Angle = document.getElementById('i_l2_angle');
const iL3Mag = document.getElementById('i_l3_mag');
const iL3Angle = document.getElementById('i_l3_angle');
const iNMag = document.getElementById('i_n_mag');
const iNAngle = document.getElementById('i_n_angle');

const resetButton = document.getElementById('resetButton');
const toggleSimulationButton = document.getElementById('toggleSimulationButton');

// Event Listeners
pDeltaSliders.forEach((slider, index) => {
    slider.addEventListener('input', () => {
        pDeltaValues[index].textContent = slider.value;
        updateSimulation();
    });
});
pYSliders.forEach((slider, index) => {
    slider.addEventListener('input', () => {
        pYValues[index].textContent = slider.value;
        updateSimulation();
    });
});

resetButton.addEventListener('click', () => {
    pDeltaSliders.forEach((slider, index) => {
        slider.value = 0;
        pDeltaValues[index].textContent = 0;
    });
    pYSliders.forEach((slider, index) => {
        slider.value = 0;
        pYValues[index].textContent = 0;
    });
    simulationTime = 0; // Reset simulation time on reset # By AI agent Mima 2026-02-05 18:40:00
    updateSimulation();
});

toggleSimulationButton.addEventListener('click', () => {
    isPaused = !isPaused; // Toggle pause state # By AI agent Mima 2026-02-05 18:40:00
    if (isPaused) {
        toggleSimulationButton.textContent = 'Resume Simulation';
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
    } else {
        toggleSimulationButton.textContent = 'Pause Simulation';
        lastUpdateTime = performance.now(); // Reset last update time on resume # By AI agent Mima 2026-02-05 18:40:00
        requestAnimationFrame(animate); // Restart animation loop # By AI agent Mima 2026-02-05 18:40:00
    }
});

// Drawing Functions
function drawPhasorDiagram(currents, neutralCurrent) {
    ctx.clearRect(0, 0, canvas.width / 2, canvas.height); // Clear left half for phasor # By AI agent Mima 2026-02-05 18:40:00
    const cx = canvas.width / 4; // Center X for phasor diagram # By AI agent Mima 2026-02-05 18:40:00
    const cy = canvas.height / 2; // Center Y for phasor diagram # By AI agent Mima 2026-02-05 18:40:00
    const axisLength = 80; // Length of reference axes # By AI agent Mima 2026-02-05 18:40:00

    // Draw axes
    ctx.strokeStyle = COLOR_AXIS;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cx - axisLength, cy);
    ctx.lineTo(cx + axisLength, cy);
    ctx.moveTo(cx, cy - axisLength);
    ctx.lineTo(cx, cy + axisLength);
    ctx.stroke();

    // Draw current phasors
    currents.forEach((current, index) => {
        const mag = current.magnitude * PHASOR_SCALE; // Scale magnitude for display # By AI agent Mima 2026-02-05 18:40:00
        const angle = current.angle + simulationTime * currentFreq; // Rotate with simulation time # By AI agent Mima 2026-02-05 18:40:00
        
        const endX = cx + mag * Math.cos(angle);
        const endY = cy - mag * Math.sin(angle); // Y-axis is inverted in canvas

        ctx.strokeStyle = [COLOR_L1, COLOR_L2, COLOR_L3][index];
        ctx.lineWidth = 3;
        drawArrow(cx, cy, endX, endY, 15); // By AI agent Mima 2026-02-05 18:40:00
    });

    // Draw neutral current phasor
    if (neutralCurrent.magnitude > 0.01) { // Only draw if significant # By AI agent Mima 2026-02-05 18:40:00
        const mag = neutralCurrent.magnitude * PHASOR_SCALE;
        const angle = neutralCurrent.angle + simulationTime * currentFreq; // Rotate with simulation time # By AI agent Mima 2026-02-05 18:40:00
        
        const endX = cx + mag * Math.cos(angle);
        const endY = cy - mag * Math.sin(angle);

        ctx.strokeStyle = COLOR_N;
        ctx.lineWidth = 4;
        drawArrow(cx, cy, endX, endY, 15); // By AI agent Mima 2026-02-05 18:40:00
    }
}

function drawSineWaves(currents, neutralCurrent) {
    ctx.clearRect(canvas.width / 2, 0, canvas.width / 2, canvas.height); // Clear right half for sine waves # By AI agent Mima 2026-02-05 18:40:00
    const offset_x = canvas.width / 2 + 50; // Start drawing sine waves after phasor # By AI agent Mima 2026-02-05 18:40:00
    const offset_y = canvas.height / 2; // Center Y for sine waves # By AI agent Mima 2026-02-05 18:40:00
    const width = canvas.width / 2 - 100; // Width for sine wave plot # By AI agent Mima 2026-02-05 18:40:00
    const height = canvas.height; // Height for sine wave plot # By AI agent Mima 2026-02-05 18:40:00
    const amplitudeScale = SINE_WAVE_HEIGHT_SCALE; // Scale for amplitude visualization # By AI agent Mima 2026-02-05 18:40:00

    // Draw horizontal axis
    ctx.strokeStyle = COLOR_AXIS;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(offset_x, offset_y);
    ctx.lineTo(offset_x + width, offset_y);
    ctx.stroke();

    // Draw sine waves
    const lineColors = [COLOR_L1, COLOR_L2, COLOR_L3, COLOR_N];
    const allCurrents = [...currents, neutralCurrent]; // Include neutral current # By AI agent Mima 2026-02-05 18:40:00

    allCurrents.forEach((current, idx) => {
        if (current.magnitude === 0) return; // Skip if no current # By AI agent Mima 2026-02-05 18:40:00

        ctx.strokeStyle = lineColors[idx];
        ctx.lineWidth = (idx === 3) ? 3 : 2; // Neutral line slightly thicker # By AI agent Mima 2026-02-05 18:40:00
        ctx.beginPath();
        
        for (let x = 0; x < width; x++) {
            const t_offset = x * 0.05; // Matches Python's t_offset # By AI agent Mima 2026-02-05 18:40:00
            const angle = current.angle + simulationTime * currentFreq + t_offset; // By AI agent Mima 2026-02-05 18:40:00
            const y_val = current.magnitude * amplitudeScale * Math.sin(angle); // Scale magnitude for display # By AI agent Mima 2026-02-05 18:40:00

            if (x === 0) {
                ctx.moveTo(offset_x + x, offset_y - y_val);
            } else {
                ctx.lineTo(offset_x + x, offset_y - y_val);
            }
        }
        ctx.stroke();
    });
}

// Helper to draw an arrow head
function drawArrow(startX, startY, endX, endY, headSize) {
    const dx = endX - startX;
    const dy = endY - startY;
    const angle = Math.atan2(dy, dx);
    const arrowAngle = Math.PI / 6;

    ctx.beginPath();
    ctx.moveTo(endX, endY);
    ctx.lineTo(endX - headSize * Math.cos(angle - arrowAngle), endY - headSize * Math.sin(angle - arrowAngle));
    ctx.lineTo(endX - headSize * Math.cos(angle + arrowAngle), endY - headSize * Math.sin(angle + arrowAngle));
    ctx.closePath();
    ctx.fill();
    ctx.stroke(); // Ensure the line leading to the arrow is also stroked # By AI agent Mima 2026-02-05 18:40:00
}

async function updateSimulation() {
    const p_y = pYSliders.map(slider => parseFloat(slider.value));
    const p_delta = pDeltaSliders.map(slider => parseFloat(slider.value));

    // Send data to Flask backend
    const response = await fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ p_y, p_delta }),
    });
    const data = await response.json();

    // Update display values
    const lineCurrents = data.line_currents;
    const neutralCurrent = data.neutral_current;

    iL1Mag.textContent = lineCurrents[0].magnitude.toFixed(1);
    iL1Angle.textContent = (lineCurrents[0].angle * 180 / Math.PI).toFixed(1);
    iL2Mag.textContent = lineCurrents[1].magnitude.toFixed(1);
    iL2Angle.textContent = (lineCurrents[1].angle * 180 / Math.PI).toFixed(1);
    iL3Mag.textContent = lineCurrents[2].magnitude.toFixed(1);
    iL3Angle.textContent = (lineCurrents[2].angle * 180 / Math.PI).toFixed(1);
    iNMag.textContent = neutralCurrent.magnitude.toFixed(1);
    iNAngle.textContent = (neutralCurrent.angle * 180 / Math.PI).toFixed(1);

    // Draw on canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear entire canvas before drawing # By AI agent Mima 2026-02-05 18:40:00
    drawPhasorDiagram(lineCurrents, neutralCurrent);
    drawSineWaves(lineCurrents, neutralCurrent);
}

function animate() {
    const currentTime = performance.now();
    const deltaTime = (currentTime - lastUpdateTime) / 1000; // in seconds # By AI agent Mima 2026-02-05 18:40:00
    lastUpdateTime = currentTime;

    if (!isPaused) {
        currentFreq = Math.min(currentFreq, MAX_FREQ); // Cap frequency # By AI agent Mima 2026-02-05 18:40:00
        simulationTime += currentFreq * deltaTime; // Update simulation time # By AI agent Mima 2026-02-05 18:40:00
        updateSimulation();
    }
    animationFrameId = requestAnimationFrame(animate);
}

// Initial setup
pDeltaSliders.forEach((slider, index) => {
    pDeltaValues[index].textContent = slider.value;
});
pYSliders.forEach((slider, index) => {
    pYValues[index].textContent = slider.value;
});

// Start the animation loop if not paused initially # By AI agent Mima 2026-02-05 18:40:00
if (!isPaused) {
    requestAnimationFrame(animate);
}

updateSimulation();
