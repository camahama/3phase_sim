import cmath
import math

VOLTAGE_RMS = 230.0
INITIAL_FREQ = 1
MAX_FREQ = 5
BASE_PIXELS_PER_AMP = 10.0


class ThreePhaseModel:
    """Pure simulation state and electrical calculations."""

    def __init__(self):
        self.time = 0.0
        self.paused = False
        self.current_freq = INITIAL_FREQ
        self.max_freq = MAX_FREQ

        self.sliders_y = [0.0, 0.0, 0.0]
        self.sliders_delta = [0.0, 0.0, 0.0]

        self.line_currents_data = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]
        self.neutral_current_data = (0.0, 0.0)

    def update_time(self, dt):
        if self.paused:
            return
        self.time += self.current_freq * dt
        self.current_freq = min(self.current_freq, self.max_freq)

    def reset_loads(self):
        self.sliders_y = [0.0, 0.0, 0.0]
        self.sliders_delta = [0.0, 0.0, 0.0]

    def toggle_pause(self):
        if self.paused:
            self.paused = False
        else:
            self.paused = True
            self.time = 0.0

    def calculate_currents(self, pixels_per_amp):
        u_phase = [
            cmath.rect(1, 0),
            cmath.rect(1, -2 * math.pi / 3),
            cmath.rect(1, -4 * math.pi / 3),
        ]
        u_line = [
            cmath.rect(1, math.pi / 6),
            cmath.rect(1, -math.pi / 2),
            cmath.rect(1, -7 * math.pi / 6),
        ]

        i_y = []
        for i in range(3):
            p = self.sliders_y[i]
            mag = p / VOLTAGE_RMS
            i_y.append(mag * u_phase[i])

        u_line_rms = VOLTAGE_RMS * math.sqrt(3)
        i_d = []
        for i in range(3):
            p = self.sliders_delta[i]
            mag = p / u_line_rms
            i_d.append(mag * u_line[i])

        i_total = [
            i_y[0] + i_d[0] - i_d[2],
            i_y[1] + i_d[1] - i_d[0],
            i_y[2] + i_d[2] - i_d[1],
        ]

        self.line_currents_data = []
        for i_ph in i_total:
            mag = abs(i_ph)
            angle = cmath.phase(i_ph)
            self.line_currents_data.append((mag * pixels_per_amp, angle))

        i_n_vec = i_total[0] + i_total[1] + i_total[2]
        self.neutral_current_data = (
            abs(i_n_vec) * pixels_per_amp,
            cmath.phase(i_n_vec),
        )
