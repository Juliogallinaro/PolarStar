"""Tests for the CNCController class in the polarstar package."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from polarstar.cnc import CNCController


@pytest.fixture
def mock_serial():
    """Fixture to mock the serial.Serial object."""
    with patch("serial.Serial") as mock_serial_class:
        mock_serial_instance = MagicMock()
        mock_serial_class.return_value = mock_serial_instance
        yield mock_serial_instance


def test_cnc_initialization(mock_serial):
    """Test the initialization of CNCController."""
    cnc = CNCController(port="COM3", baudrate=9600, timeout=2)
    assert cnc.port == "COM3"
    assert cnc.baudrate == 9600
    assert cnc.timeout == 2
    assert cnc.callbacks == {}


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
    # Initialize CNCController
    cnc = CNCController(port="COM3", baudrate=9600)

    # Mock Arduino serial connection
    arduino_mock = MagicMock()

    # Define the callback
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
        label = line.split("at")[1].strip()  # Extract the label
        assert label in ["A1", "A2"]  # Ensure the label is expected

        # Validate the arguments are correct
        assert delay == 1
        assert pwm_value == 128
        assert arduino_serial == arduino_mock
        assert csv_filename == "data.csv"
        assert mouse_position == (100, 200)
        assert num_measurements == 10

        # Simulate Arduino interactions
        arduino_serial.write(b"128\n")  # Simulate sending the PWM value
        arduino_serial.write(b"0\n")  # Simulate resetting the PWM

        # Call the mocked data collection function
        collect_data_and_save_to_csv(
            csv_filename, mouse_position, label, num_measurements
        )

    # Register the callback
    cnc.register_callback(
        "Read",  # Activate the callback for "Read" commands
        on_read_command_mock,
        delay=1,
        pwm_value=128,
        arduino_serial=arduino_mock,
        csv_filename="data.csv",
        mouse_position=(100, 200),
        num_measurements=10,
    )

    # Simulate the G-code
    gcode = """\
        G0 X0.00 Y-90.00 Z0.00 ; Move to above well at (0, 0)
        G0 Z20.00 ; Lower to reading height
        Read well at A1
        G0 Z0.00 ; Raise back to safe height
        G0 X39.00 Y-90.00 Z0.00 ; Move to above well at (0, 1)
        G0 Z20.00 ; Lower to reading height
        Read well at A2
        """

    # Simulate CNC responses
    mock_serial.readline.side_effect = [
        b"<Idle>\n",
        b"ok\n",
    ] * 20  # Alternate <Idle> and ok

    # Execute the G-code
    cnc.send_gcode(gcode)

    # Validate that the Arduino mock received the correct calls
    arduino_mock.write.assert_any_call(b"128\n")
    arduino_mock.write.assert_any_call(b"0\n")

    # Ensure the data collection function was called twice (for A1 and A2)
    assert arduino_mock.write.call_count == 4  # Two "128" and two "0"
