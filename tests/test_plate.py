"""Unit tests for the Plate class and related functions in the polarstar package.

This module provides comprehensive testing of all Plate class functionality including
initialization, data handling, string representation, row labeling, and plotting.
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


@pytest.fixture
def filled_plate():
    """Fixture to create a plate with some test data."""
    plate = Plate(2, 3)
    plate.set_custom("A1", 1.5, "Substance1", "blue")
    plate.set_serial_dilutions("A2", 1.0, 2.0, 2, "Substance2", "red")
    return plate


def test_initialization(plate):
    """Test that the plate is initialized correctly with empty wells."""
    assert plate.rows == 2
    assert plate.cols == 3
    assert plate.data.shape == (2, 3)
    assert np.all(np.equal(plate.data, None))

    # Test default parameters
    assert plate.x_spacing == 9
    assert plate.y_spacing == 9
    assert plate.z_read == -5
    assert plate.z_safe == 0
    assert plate.offset_y == -90
    assert plate.offset_z == -5
    assert plate.diameter == 6.94


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


@pytest.mark.parametrize(
    "concentration, expected_display, expected_unit",
    [
        (1e1, 10.0, "mM"),
        (5e0, 5.0, "mM"),
        (1e-2, 0.01, "mM"),
        (5e-3, 5.0, "µM"),
        (1e-5, 0.01, "µM"),
        (5e-6, 5.0, "nM"),
        (1e-8, 0.01, "nM"),
        (5e-9, 5.0, "pM"),
    ],
)
def test_convert_concentration(plate, concentration, expected_display, expected_unit):
    """Test concentration conversion to readable units with input in mM."""
    display, unit = plate.convert_concentration(concentration)
    assert display == expected_display
    assert unit == expected_unit


def test_set_serial_dilutions(plate):
    """Test filling the plate with serial dilutions."""
    plate.set_serial_dilutions("A1", 1.0, 10.0, 6, "Substance", "blue")
    assert plate.data[0, 0] == ("A1", "Substance", "blue", 1.00, "mM")
    assert plate.data[0, 1] == ("A2", "Substance", "blue", 0.10, "mM")
    assert plate.data[0, 2] == ("A3", "Substance", "blue", 0.01, "mM")
    assert plate.data[1, 0] == ("B1", "Substance", "blue", 1.00, "µM")
    assert plate.data[1, 1] == ("B2", "Substance", "blue", 0.10, "µM")
    assert plate.data[1, 2] == ("B3", "Substance", "blue", 0.01, "µM")


def test_set_custom(plate):
    """Test filling a specific well with a custom value."""
    plate.set_custom("B2", 2.5, "Substance2", "green")
    assert plate.data[1, 1] == ("B2", "Substance2", "green", 2.5, "")


def test_save_and_load(plate, tmp_path):
    """Test saving and loading plate data."""
    # Fill plate with test data
    plate.set_custom("A1", 2.5, "TestSubstance", "green")
    filename = str(tmp_path / "test_plate")

    # Save plate
    saved_path = plate.save(filename)
    assert saved_path.endswith(".star")

    # Load plate
    loaded_plate = load_plate(saved_path)
    assert loaded_plate.rows == plate.rows
    assert loaded_plate.cols == plate.cols
    assert np.array_equal(loaded_plate.data, plate.data)


def test_str_representation(filled_plate):
    """Test string representation of the plate."""
    str_rep = str(filled_plate)
    assert isinstance(str_rep, str)
    assert "Substance1" in str_rep
    assert "Substance2" in str_rep
    assert "Empty" in str_rep


def test_index_to_row_label(plate):
    """Test conversion of numeric indices to alphabetic row labels."""
    assert plate.index_to_row_label(0) == "B"
    assert plate.index_to_row_label(1) == "A"

    # Test with larger plate
    large_plate = Plate(27, 3)  # Test multi-letter labels
    assert large_plate.index_to_row_label(0) == "AA"
    assert large_plate.index_to_row_label(25) == "B"
    assert large_plate.index_to_row_label(26) == "A"


def test_generate_gcode_empty_plate(plate):
    """Test G-code generation for empty plate."""
    gcode = plate.generate_gcode()
    assert "G21" in gcode  # Check units setting
    assert "G90" in gcode  # Check absolute positioning
    assert "M30" in gcode  # Check program end

    # Empty plate should not have any well readings
    assert "Read well" not in gcode


def test_generate_gcode_with_data(filled_plate):
    """Test G-code generation for plate with data."""
    gcode = filled_plate.generate_gcode()

    # Check basic G-code structure
    assert "G21" in gcode
    assert "G90" in gcode

    # Check well movements
    assert "Read well at A1" in gcode
    assert "Read well at A2" in gcode

    # Check safe height movements
    assert f"Z{-filled_plate.z_safe:.2f}" in gcode
    assert f"Z{-filled_plate.z_read:.2f}" in gcode


def test_plot_plate_with_data(filled_plate):
    """Test plotting functionality with data."""
    matplotlib.use("Agg")
    try:
        # Test plotting with different parameters
        filled_plate.plot_plate(
            figsize=(10, 6),
            show_concentration=True,
            well_font_size=8,
            legend_font_size=8,
            tick_font_size=6,
        )

        # Test plotting without concentrations
        filled_plate.plot_plate(show_concentration=False)
    finally:
        matplotlib.pyplot.close("all")


def test_edge_cases():
    """Test edge cases and potential error conditions."""
    # Test 1x1 plate
    tiny_plate = Plate(1, 1)
    tiny_plate.set_custom("A1", 1.0, "Test", "red")
    assert tiny_plate.data[0, 0] == ("A1", "Test", "red", 1.0, "")

    # Test larger plate
    large_plate = Plate(8, 12)  # Standard 96-well plate
    assert large_plate.rows == 8
    assert large_plate.cols == 12

    # Test serial dilution beyond plate bounds
    large_plate.set_serial_dilutions("A1", 1.0, 2.0, 15, "Test", "blue")
    # Should only fill up to available wells
    assert large_plate.data[0, 11] is not None  # Last well in first row

    # Test custom position beyond bounds
    large_plate.set_custom("I1", 1.0, "Test", "red")  # Beyond rows
    assert np.all(
        large_plate.data[7, :] == large_plate.data[7, :]
    )  # Last row unchanged
