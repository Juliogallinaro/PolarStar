"""Unit tests for the Plate class and related functions in the polarstar package.

This module tests functionalities such as initialization, data handling,
concentration conversions, serial dilutions, G-code generation,
and saving/loading of plate data.
"""

import matplotlib
import numpy as np
import pytest

from polarstar import Plate
from polarstar import load_plate


@pytest.fixture
def plate():
    """Fixture to create a 2x3 plate for testing."""
    return Plate(2, 3)


def test_initialization(plate):
    """Test that the plate is initialized correctly with empty wells."""
    assert plate.rows == 2
    assert plate.cols == 3
    assert plate.data.shape == (2, 3)
    assert np.all(np.equal(plate.data, None))


def test_pos_to_index(plate):
    """Test conversion from (row, col) position to linear index."""
    assert plate.pos_to_index(0, 0) == 0
    assert plate.pos_to_index(0, 1) == 1
    assert plate.pos_to_index(0, 2) == 2
    assert plate.pos_to_index(1, 0) == 3
    assert plate.pos_to_index(1, 1) == 4
    assert plate.pos_to_index(1, 2) == 5


def test_index_to_pos(plate):
    """Test conversion from linear index to (row, col) position."""
    assert plate.index_to_pos(0) == (0, 0)
    assert plate.index_to_pos(1) == (0, 1)
    assert plate.index_to_pos(2) == (0, 2)
    assert plate.index_to_pos(3) == (1, 0)
    assert plate.index_to_pos(4) == (1, 1)
    assert plate.index_to_pos(5) == (1, 2)


# Define the test values and expected outputs
@pytest.mark.parametrize(
    "concentration, expected_display, expected_unit",
    [
        (1e1, 10.0, "mM"),  # Input: 1e+01 mM -> Display: 10.0 mM
        (5e0, 5.0, "mM"),  # Input: 5e+00 mM -> Display: 5.0 mM
        (1e-2, 0.01, "mM"),  # Input: 1e-02 mM -> Display: 0.01 mM
        (5e-3, 5.0, "µM"),  # Input: 5e-03 mM -> Display: 5.0 µM
        (1e-5, 0.01, "µM"),  # Input: 1e-05 mM -> Display: 0.01 µM
        (5e-6, 5.0, "nM"),  # Input: 5e-06 mM -> Display: 5.0 nM
        (1e-8, 0.01, "nM"),  # Input: 1e-08 mM -> Display: 0.01 nM
        (5e-9, 5.0, "pM"),  # Input: 5e-09 mM -> Display: 5.0 pM
    ],
)
def test_convert_concentration(plate, concentration, expected_display, expected_unit):
    """Test concentration conversion to readable units with input in mM."""
    display, unit = plate.convert_concentration(concentration)
    assert display == expected_display, (
        f"Expected {expected_display} for {concentration:.0e} mM, " f"but got {display}"
    )
    assert unit == expected_unit, (
        f"Expected unit {expected_unit} for {concentration:.0e} mM, " f"but got {unit}"
    )


def test_fill_serial_dilutions(plate):
    """Test filling the plate with serial dilutions."""
    plate.fill_serial_dilutions("A1", 1.0, 10.0, 6, "Substance", "blue")
    assert plate.data[0, 0] == ("A1", "Substance", "blue", 1.00, "mM")
    assert plate.data[0, 1] == ("A2", "Substance", "blue", 0.10, "mM")
    assert plate.data[0, 2] == ("A3", "Substance", "blue", 0.01, "mM")
    assert plate.data[1, 0] == ("B1", "Substance", "blue", 1.00, "µM")
    assert plate.data[1, 1] == ("B2", "Substance", "blue", 0.10, "µM")
    assert plate.data[1, 2] == ("B3", "Substance", "blue", 0.01, "µM")


def test_fill_custom(plate):
    """Test filling a specific well with a custom value."""
    plate.fill_custom("B2", 2.5, "Substance2", "green")
    assert plate.data[1, 1] == ("B2", "Substance2", "green", 2.5, "")


def test_save(plate, tmp_path, capsys):
    """Test the save method to ensure it saves plate data correctly and prints confirmation."""
    # Arrange: Define the filename and expected file path
    filename = tmp_path / "test_plate"
    expected_path = f"{filename}.star"

    # Act: Fill the plate with some data, then save
    plate.fill_custom(
        "A1", 2.5, "TestSubstance", "green"
    )  # Fill one well with sample data
    saved_path = plate.save(str(filename))

    # Capture printed output
    captured = capsys.readouterr()

    # Assert: Check the return value of the save function
    assert (
        saved_path == expected_path
    ), f"Expected saved path {expected_path}, but got {saved_path}"

    # Assert: Verify the file was created
    assert tmp_path.joinpath(
        expected_path
    ).exists(), f"Expected file at {expected_path} not found."

    # Assert: Verify the content of the saved file
    with open(expected_path, "rb") as f:
        saved_data = np.load(f, allow_pickle=True)
    assert np.array_equal(
        saved_data, plate.data
    ), "Saved data does not match plate data."

    # Assert: Check that the correct print message was output
    expected_message = f"Data successfully saved to {expected_path}\n"
    assert (
        captured.out == expected_message
    ), f"Expected message {expected_message!r}, but got {captured.out!r}"


def test_generate_gcode(plate):
    """Test G-code generation for CNC movement over the wells."""
    plate.fill_custom("A1", 1.5, "TestSubstance", "blue")
    gcode = plate.generate_gcode()
    assert "G21; Set units to millimeters" in gcode
    assert "G90; Use absolute positioning" in gcode
    assert "G0 X0.00 Y-90.00 Z0.00" in gcode
    assert "Read well at A1" in gcode


def test_load_plate(tmp_path):
    """Test the load_plate function to ensure it loads plate data correctly from a file."""
    # Arrange: Create a sample plate, fill with data, and save
    original_plate = Plate(2, 3)
    original_plate.fill_custom("A1", 2.5, "TestSubstance", "green")
    filename = tmp_path / "test_plate.star"
    original_plate.save(str(filename))

    # Act: Load the plate using the load_plate function
    loaded_plate = load_plate(str(filename))

    # Assert: Verify the loaded plate dimensions
    assert (
        loaded_plate.rows == original_plate.rows
    ), "Loaded plate row count does not match original."
    assert (
        loaded_plate.cols == original_plate.cols
    ), "Loaded plate column count does not match original."

    # Assert: Verify the loaded data matches the original plate data
    assert np.array_equal(
        loaded_plate.data, original_plate.data
    ), "Loaded plate data does not match original data."


@pytest.mark.usefixtures("plate")
def test_plot_plate_no_data(plate):
    """Test plot_plate with no data in wells."""
    # Temporarily set the backend to 'Agg' to prevent window opening
    matplotlib.use("Agg")
    try:
        # Test if plot_plate can handle an empty plate without opening a window
        plate.plot_plate()  # Should not raise errors, even if all wells are empty
    finally:
        # Close all open figures
        matplotlib.pyplot.close("all")
