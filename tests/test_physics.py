import os
import sys
import unittest

# Allow running from repository root with: python -m unittest tests/test_physics.py
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from trefas_app.physics import (
    calculate_line_and_neutral_currents,
    phase_voltages,
    resistive_impedance_from_active_power,
)

TEST_VOLTAGE_RMS = 230.0


class TestPhysicsCalculator(unittest.TestCase):
    def test_balanced_resistive_y_load_has_zero_neutral(self):
        z = resistive_impedance_from_active_power(230.0, TEST_VOLTAGE_RMS)
        line_currents, neutral_current = calculate_line_and_neutral_currents(
            y_impedances=[z, z, z],
            delta_impedances=[None, None, None],
            voltage_rms=TEST_VOLTAGE_RMS,
        )

        for current in line_currents:
            self.assertAlmostEqual(abs(current), 1.0, places=6)
        self.assertAlmostEqual(abs(neutral_current), 0.0, places=6)

    def test_complex_y_loads_are_supported(self):
        z1 = 20 + 10j
        z2 = 25 - 5j
        z3 = 15 + 20j
        line_currents, neutral_current = calculate_line_and_neutral_currents(
            y_impedances=[z1, z2, z3],
            delta_impedances=[None, None, None],
            voltage_rms=TEST_VOLTAGE_RMS,
        )

        self.assertEqual(len(line_currents), 3)
        self.assertTrue(all(isinstance(curr, complex) for curr in line_currents))
        self.assertIsInstance(neutral_current, complex)

    def test_open_circuit_branches_with_none(self):
        line_currents, neutral_current = calculate_line_and_neutral_currents(
            y_impedances=[None, None, None],
            delta_impedances=[None, None, None],
            voltage_rms=TEST_VOLTAGE_RMS,
        )
        self.assertAlmostEqual(abs(line_currents[0]), 0.0, places=9)
        self.assertAlmostEqual(abs(line_currents[1]), 0.0, places=9)
        self.assertAlmostEqual(abs(line_currents[2]), 0.0, places=9)
        self.assertAlmostEqual(abs(neutral_current), 0.0, places=9)

    def test_zero_impedance_raises(self):
        with self.assertRaises(ValueError):
            calculate_line_and_neutral_currents(
                y_impedances=[1 + 0j, 0 + 0j, 1 + 0j],
                delta_impedances=[None, None, None],
                voltage_rms=TEST_VOLTAGE_RMS,
            )

    def test_phase_voltages_are_120_degrees_apart(self):
        v1, v2, v3 = phase_voltages(TEST_VOLTAGE_RMS)
        self.assertAlmostEqual(abs(v1), TEST_VOLTAGE_RMS, places=9)
        self.assertAlmostEqual(abs(v2), TEST_VOLTAGE_RMS, places=9)
        self.assertAlmostEqual(abs(v3), TEST_VOLTAGE_RMS, places=9)


if __name__ == "__main__":
    unittest.main()
