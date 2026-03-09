import cmath

from .physics import (
    calculate_line_and_neutral_currents,
    line_voltages,
    resistive_impedance_from_active_power,
)

VOLTAGE_RMS = 230.0
INITIAL_FREQ = 1
MAX_FREQ = 5
BASE_CURRENT_SCALE = 10.0


class ThreePhaseModel:
    """Simulation state wrapper around the pure physics calculator."""

    def __init__(self):
        self.time = 0.0
        self.paused = False
        self.current_freq = INITIAL_FREQ
        self.max_freq = MAX_FREQ

        self.phase_active_powers_w = [0.0, 0.0, 0.0]
        self.delta_active_powers_w = [0.0, 0.0, 0.0]

        self.line_currents_data = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]
        self.neutral_current_data = (0.0, 0.0)

    def update_time(self, dt):
        if self.paused:
            return
        self.time += self.current_freq * dt
        self.current_freq = min(self.current_freq, self.max_freq)

    def reset_loads(self):
        self.phase_active_powers_w = [0.0, 0.0, 0.0]
        self.delta_active_powers_w = [0.0, 0.0, 0.0]

    def set_active_powers(self, phase_powers_w, delta_powers_w):
        if len(phase_powers_w) != 3:
            raise ValueError("phase_powers_w must contain exactly three elements")
        if len(delta_powers_w) != 3:
            raise ValueError("delta_powers_w must contain exactly three elements")

        self.phase_active_powers_w = list(phase_powers_w)
        self.delta_active_powers_w = list(delta_powers_w)

    def toggle_pause(self):
        if self.paused:
            self.paused = False
        else:
            self.paused = True
            self.time = 0.0

    def calculate_currents(self, pixels_per_amp):
        vp = VOLTAGE_RMS
        vl = abs(line_voltages(VOLTAGE_RMS)[0])

        y_impedances = [
            resistive_impedance_from_active_power(power_w, vp)
            for power_w in self.phase_active_powers_w
        ]
        delta_impedances = [
            resistive_impedance_from_active_power(power_w, vl)
            for power_w in self.delta_active_powers_w
        ]

        line_currents, neutral_current = calculate_line_and_neutral_currents(
            y_impedances=y_impedances,
            delta_impedances=delta_impedances,
            voltage_rms=VOLTAGE_RMS,
        )

        self.line_currents_data = [
            (abs(curr) * pixels_per_amp, cmath.phase(curr)) for curr in line_currents
        ]
        self.neutral_current_data = (
            abs(neutral_current) * pixels_per_amp,
            cmath.phase(neutral_current),
        )
