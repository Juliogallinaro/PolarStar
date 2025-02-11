"""Tests for the CNCController class in the polarstar package."""

from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

import numpy as np
import pytest

from polarstar.cnc import CNCController
from polarstar.cnc import create_circle_points
from polarstar.plate import Plate  # Adding import for Plate class


@pytest.fixture
def mock_serial():
    """Fixture to mock the serial.Serial object."""
    with patch("serial.Serial") as mock_serial_class:
        mock_serial_instance = MagicMock()
        mock_serial_class.return_value = mock_serial_instance
        yield mock_serial_instance


@pytest.fixture
def mock_plate():
    """Fixture to create a mock Plate object."""
    plate = MagicMock(spec=Plate)
    plate.generate_gcode.return_value = "G1 X10 Y10\nG1 X20 Y20"
    plate.rows = 2
    plate.cols = 3
    plate.x_spacing = 10
    plate.y_spacing = 10
    plate.offset_y = 5
    plate.offset_z = 0
    plate.diameter = 8
    plate.data = np.full((2, 3), None)
    return plate


def test_create_circle_points():
    """Test creation of circle points."""
    center = [0, 0, 0]
    radius = 10
    x, y, z = create_circle_points(center, radius, num_points=100)

    assert len(x) == 100
    assert len(y) == 100
    assert len(z) == 100
    assert np.allclose(z, 0)

    # Test circle properties
    distances = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
    assert np.allclose(distances, radius, rtol=1e-10)


def test_send_gcode_with_file(mock_serial, tmp_path):
    """Test sending G-code from a file."""
    gcode_content = "G1 X10 Y10\nG1 X20 Y20"
    gcode_file = tmp_path / "test.gcode"
    gcode_file.write_text(gcode_content)

    controller = CNCController()
    mock_serial.readline.return_value = b"ok\n"

    controller.send_gcode(str(gcode_file))

    assert mock_serial.write.call_count == 2
    mock_serial.write.assert_any_call(b"G1 X10 Y10\n")
    mock_serial.write.assert_any_call(b"G1 X20 Y20\n")


def test_send_gcode_with_plate(mock_serial, mock_plate):
    """Test sending G-code generated from a Plate object."""
    controller = CNCController()
    mock_serial.readline.return_value = b"ok\n"

    controller.send_gcode(mock_plate)

    mock_plate.generate_gcode.assert_called_once()
    assert mock_serial.write.call_count == 2


def test_serial_communication_error(mock_serial):
    """Test handling of serial communication errors."""
    controller = CNCController()
    mock_serial.write.side_effect = Exception("Serial error")

    with pytest.raises(Exception, match="Serial error"):
        controller.send_gcode("G1 X10 Y10")


def test_wait_for_idle_basic(mock_serial):
    """Test basic idle state detection."""
    controller = CNCController()

    # Simulate machine becoming idle after two checks
    mock_serial.readline.side_effect = [b"<Run>\n", b"<Run>\n", b"<Idle>\n"]

    controller.wait_for_idle(mock_serial)

    # Should have sent status check command three times
    assert mock_serial.write.call_count == 3
    mock_serial.write.assert_called_with(b"?")


def test_wait_for_idle_with_status_variations(mock_serial):
    """Test idle detection with various machine status responses."""
    controller = CNCController()

    # Test different status messages before idle
    mock_serial.readline.side_effect = [
        b"<Alarm>\n",
        b"<Home>\n",
        b"<Run>\n",
        b"<Hold:0>\n",
        b"<Door:0>\n",
        b"<Idle>\n",
    ]

    controller.wait_for_idle(mock_serial)

    assert mock_serial.write.call_count == 6
    mock_serial.write.assert_called_with(b"?")


def test_wait_for_idle_with_error_response(mock_serial):
    """Test idle detection with error responses."""
    controller = CNCController()

    # Simulate error responses before idle
    mock_serial.readline.side_effect = [
        b"error:20\n",  # Generic error
        b"<Run>\n",
        b"ALARM:1\n",  # Alarm state
        b"<Run>\n",
        b"<Idle>\n",
    ]

    controller.wait_for_idle(mock_serial)

    assert mock_serial.write.call_count == 5
    mock_serial.write.assert_called_with(b"?")


def test_wait_for_idle_with_malformed_responses(mock_serial):
    """Test idle detection with malformed status responses."""
    controller = CNCController()

    # Test handling of malformed responses
    mock_serial.readline.side_effect = [
        b"",  # Empty response
        b"garbage\n",  # Invalid response
        b"<partial",  # Incomplete status
        b"<Run>\n",
        b"<Idle>\n",
    ]

    controller.wait_for_idle(mock_serial)

    assert mock_serial.write.call_count == 5
    mock_serial.write.assert_called_with(b"?")


def test_send_gcode_with_serial_dilutions(mock_serial, mock_plate):
    """Test sending G-code for a plate with serial dilutions."""
    controller = CNCController()
    mock_serial.readline.return_value = b"ok\n"

    # Define expected G-code for serial dilutions
    expected_gcode = """G21; Set units to millimeters
G90; Use absolute positioning
G0 Z-10.00
G0 X0.00 Y-80.00 Z-10.00; Move to above well at (0, 0)
G0 Z5.00; Lower to reading height
Read well at A1
G0 Z-10.00; Raise back to safe height
G0 X39.00 Y-80.00 Z-10.00; Move to above well at (0, 1)
G0 Z5.00; Lower to reading height
Read well at A2
G0 Z-10.00; Raise back to safe height
G0 X78.00 Y-80.00 Z-10.00; Move to above well at (0, 2)
G0 Z5.00; Lower to reading height
Read well at A3
G0 Z-10.00; Raise back to safe height
G0 X0.00 Y-41.00 Z-10.00; Move to above well at (1, 0)
G0 Z5.00; Lower to reading height
Read well at B1
G0 Z-10.00; Raise back to safe height
G0 X39.00 Y-41.00 Z-10.00; Move to above well at (1, 1)
G0 Z5.00; Lower to reading height
Read well at B2
G0 Z-10.00; Raise back to safe height
G0 X78.00 Y-41.00 Z-10.00; Move to above well at (1, 2)
G0 Z5.00; Lower to reading height
Read well at B3
G0 Z-10.00; Raise back to safe height
G0 X0 Y0; Return
G0 Z0; Return
M30; End of program"""

    # Configure mock plate
    mock_plate.generate_gcode.return_value = expected_gcode

    # Set up serial dilutions
    mock_plate.set_serial_dilutions(
        start_pos="A1",
        initial_concentration=5,
        dilution_factor=5,
        num_dilutions=2,
        substance="Fluorescein",
        color="green",
    )

    mock_plate.set_serial_dilutions(
        start_pos="B1",
        initial_concentration=5,
        dilution_factor=5,
        num_dilutions=2,
        substance="Rhodamine B",
        color="red",
    )

    # Set custom values
    mock_plate.set_custom(pos="A3", value="Blank", substance="Blank", color="blue")
    mock_plate.set_custom(pos="B3", value="Blank", substance="Blank", color="blue")

    # Send G-code and verify
    controller.send_gcode(mock_plate)

    # Verify each G-code line was sent
    expected_lines = expected_gcode.split("\n")
    assert mock_serial.write.call_count == len(expected_lines)

    for line in expected_lines:
        if line.strip():  # Skip empty lines
            mock_serial.write.assert_any_call(f"{line}\n".encode())


def test_send_gcode(mock_serial):
    """Test sending G-code commands."""
    cnc = CNCController(port="COM3", baudrate=9600)

    # Example G-code
    gcode = "G21\nG90\nG1 X10 Y10 F300\n"

    # Simulate the CNC machine responding with "ok"
    mock_serial.readline.side_effect = [b"ok\n", b"ok\n", b"ok\n"]

    # Call the method
    cnc.send_gcode(gcode)

    # Verify the G-code lines were sent correctly
    mock_serial.write.assert_any_call(b"G21\n")
    mock_serial.write.assert_any_call(b"G90\n")
    mock_serial.write.assert_any_call(b"G1 X10 Y10 F300\n")


def test_register_callback():
    """Test registering a callback."""
    cnc = CNCController()

    def mock_callback(command, *args, **kwargs):
        print(f"Callback executed for: {command}")

    cnc.register_callback("G1", mock_callback, "extra_arg", key="value")

    assert "g1" in cnc.callbacks
    callback, args, kwargs = cnc.callbacks["g1"]
    assert callback == mock_callback
    assert args == ("extra_arg",)
    assert kwargs == {"key": "value"}


def collect_data_and_save_to_csv(csv_filename, mouse_position, label, num_measurements):
    """Mock implementation of the collect_data_and_save_to_csv function."""
    print(
        f"Data collected: {csv_filename}, {mouse_position}, {label}, {num_measurements}"
    )


def test_callback_execution(mock_serial):
    """Test callback execution during G-code sending."""
    cnc = CNCController(port="COM3", baudrate=9600)
    arduino_mock = MagicMock()

    def on_read_command_mock(
        line,
        delay,
        pwm_value,
        arduino_serial,
        csv_filename,
        mouse_position,
        num_measurements,
    ):
        assert "Read well at" in line
        label = line.split("at")[1].strip()
        assert label in ["A1", "A2"]

        assert delay == 1
        assert pwm_value == 128
        assert arduino_serial == arduino_mock
        assert csv_filename == "data.csv"
        assert mouse_position == (100, 200)
        assert num_measurements == 10

        arduino_serial.write(str(pwm_value).encode() + b"\n")
        arduino_serial.write(b"0\n")

        collect_data_and_save_to_csv(
            csv_filename, mouse_position, label, num_measurements
        )

    cnc.register_callback(
        "Read",
        on_read_command_mock,
        delay=1,
        pwm_value=128,
        arduino_serial=arduino_mock,
        csv_filename="data.csv",
        mouse_position=(100, 200),
        num_measurements=10,
    )

    gcode = """\
        G0 X0.00 Y-90.00 Z0.00 ; Move to above well at (0, 0)
        G0 Z20.00 ; Lower to reading height
        Read well at A1
        G0 Z0.00 ; Raise back to safe height
        G0 X39.00 Y-90.00 Z0.00 ; Move to above well at (0, 1)
        G0 Z20.00 ; Lower to reading height
        Read well at A2
        """

    mock_serial.readline.side_effect = [b"<Idle>\n", b"ok\n"] * 20

    cnc.send_gcode(gcode)

    # Verify all Arduino mock calls in sequence
    expected_calls = [call(b"128\n"), call(b"0\n"), call(b"128\n"), call(b"0\n")]
    assert arduino_mock.write.call_args_list == expected_calls
    assert arduino_mock.write.call_count == 4
