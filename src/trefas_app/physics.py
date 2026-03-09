import cmath
import math

def phase_voltages(voltage_rms):
    """Return L1/L2/L3 phase-to-neutral voltages as complex RMS phasors."""
    return (
        voltage_rms * cmath.rect(1, 0),
        voltage_rms * cmath.rect(1, -2 * math.pi / 3),
        voltage_rms * cmath.rect(1, -4 * math.pi / 3),
    )


def line_voltages(voltage_rms):
    """Return V12/V23/V31 line-to-line voltages as complex RMS phasors."""
    v1, v2, v3 = phase_voltages(voltage_rms)
    return (v1 - v2, v2 - v3, v3 - v1)


def _safe_current(voltage, impedance):
    """Return I = V/Z while handling open-circuit loads."""
    if impedance is None:
        return 0j
    if abs(impedance) < 1e-12:
        raise ValueError("Impedance magnitude must be > 0")
    return voltage / impedance


def calculate_line_and_neutral_currents(
    y_impedances,
    delta_impedances=None,
    voltage_rms=None,
):
    """Calculate line and neutral currents from complex Y and Delta impedances.

    Args:
        y_impedances: Iterable with three complex impedances [Z1N, Z2N, Z3N].
        delta_impedances: Optional iterable with three complex impedances
            [Z12, Z23, Z31]. Use None for an open branch.
        voltage_rms: Phase-to-neutral RMS voltage magnitude.

    Returns:
        tuple: (line_currents, neutral_current)
            line_currents: (I1, I2, I3) complex RMS currents.
            neutral_current: complex RMS current.
    """
    if voltage_rms is None:
        raise ValueError("voltage_rms is required")

    if len(y_impedances) != 3:
        raise ValueError("y_impedances must contain exactly three elements")

    if delta_impedances is None:
        delta_impedances = (None, None, None)
    if len(delta_impedances) != 3:
        raise ValueError("delta_impedances must contain exactly three elements")

    vp = phase_voltages(voltage_rms)
    vl = line_voltages(voltage_rms)

    i_y = [
        _safe_current(vp[idx], y_impedances[idx]) for idx in range(3)
    ]

    i_delta = [
        _safe_current(vl[idx], delta_impedances[idx]) for idx in range(3)
    ]

    i_line = (
        i_y[0] + i_delta[0] - i_delta[2],
        i_y[1] + i_delta[1] - i_delta[0],
        i_y[2] + i_delta[2] - i_delta[1],
    )
    i_neutral = i_line[0] + i_line[1] + i_line[2]

    return i_line, i_neutral


def resistive_impedance_from_active_power(power_w, voltage_rms):
    """Convert resistive active power to equivalent real impedance.

    Returns None for power <= 0, which can be treated as an open branch.
    """
    if power_w <= 0:
        return None
    return (voltage_rms ** 2) / power_w
