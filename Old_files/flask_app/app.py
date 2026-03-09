from flask import Flask, render_template, request, jsonify
import cmath
import math

# By AI agent Mima 2026-02-05 18:35:00: Flask application for 3-phase simulation
app = Flask(__name__)

# --- Physics Parameters (extracted from original main.py) ---
VOLTAGE_RMS = 230.0 # By AI agent Mima 2026-02-05 18:35:00

# By AI agent Mima 2026-02-05 18:35:00: Adapted calculate_currents function
def calculate_currents(p_y_values, p_delta_values):
    # Base voltage phasors for Y-connection (L1, L2, L3 relative to Neutral)
    # These are unit vectors representing the phase angles
    u_phase = [
        cmath.rect(1, 0),                        # L1: 0 degrees
        cmath.rect(1, -2 * math.pi / 3),         # L2: -120 degrees
        cmath.rect(1, -4 * math.pi / 3)          # L3: -240 degrees (or +120 degrees)
    ]
    
    # Base voltage phasors for Delta-connection (Line-to-Line)
    # These are unit vectors representing the phase angles of line voltages
    u_line = [
        cmath.rect(1, math.pi / 6),              # U12: 30 degrees (L1-L2)
        cmath.rect(1, -math.pi / 2),             # U23: -90 degrees (L2-L3)
        cmath.rect(1, -7 * math.pi / 6)          # U31: -210 degrees (L3-L1)
    ]
    
    # Calculate currents for Y-connected loads
    i_y = []
    for i in range(3):
        p = p_y_values[i]
        if p < 0: p = 0 # Ensure power is non-negative
        mag = p / VOLTAGE_RMS if VOLTAGE_RMS != 0 else 0
        i_y.append(mag * u_phase[i])
            
    # Calculate line-to-line RMS voltage for Delta connection
    u_line_rms = VOLTAGE_RMS * math.sqrt(3)
    
    # Calculate currents for Delta-connected loads
    i_d = []
    for i in range(3):
        p = p_delta_values[i]
        if p < 0: p = 0 # Ensure power is non-negative
        mag = p / u_line_rms if u_line_rms != 0 else 0
        i_d.append(mag * u_line[i])
        
    # Calculate total line currents (Kirchhoff's current law at the nodes)
    # iL1 = iY1 + iD1 - iD3 (current from L1 to L2, minus current from L3 to L1)
    # iL2 = iY2 + iD2 - iD1
    # iL3 = iY3 + iD3 - iD2
    i_total = [
        i_y[0] + i_d[0] - i_d[2],
        i_y[1] + i_d[1] - i_d[0],
        i_y[2] + i_d[2] - i_d[1]
    ]
    
    line_currents_data = []
    for i_ph in i_total:
        mag = abs(i_ph)
        angle = cmath.phase(i_ph)
        line_currents_data.append({'magnitude': mag, 'angle': angle})
            
    # Calculate neutral current (sum of all line currents)
    i_n_vec = (i_total[0] + i_total[1] + i_total[2])
    neutral_current_data = {'magnitude': abs(i_n_vec), 'angle': cmath.phase(i_n_vec)}

    return {
        'line_currents': line_currents_data,
        'neutral_current': neutral_current_data
    }

# By AI agent Mima 2026-02-05 18:35:00: Main route to render the HTML template
@app.route('/')
def index():
    return render_template('index.html')

# By AI agent Mima 2026-02-05 18:35:00: API endpoint for current calculation
@app.route('/calculate', methods=['POST'])
def get_currents():
    data = request.json
    p_y_values = data.get('p_y', [0.0, 0.0, 0.0])
    p_delta_values = data.get('p_delta', [0.0, 0.0, 0.0])
    
    results = calculate_currents(p_y_values, p_delta_values)
    return jsonify(results)

# By AI agent Mima 2026-02-05 18:35:00: Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
