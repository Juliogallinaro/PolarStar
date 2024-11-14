"""Module for managing plates.

This module provides the Plate class, which includes methods for storing
and organizing substances in a multi-well plate format, performing serial dilutions,
custom well configurations, and generating G-code for automated CNC
movements over the wells.
"""

from typing import Optional
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D  # type: ignore
from matplotlib.patches import Circle  # type: ignore


class Plate:
    """Class representing a plate for storing substances, concentrations or custom information.

    Parameters
    ----------
    rows : int
        Number of rows in the plate.
    cols : int
        Number of columns in the plate.
    """

    def __init__(self, rows: int, cols: int) -> None:
        """Initialize a plate for storing substances, concentrations, or custom information.

        Parameters
        ----------
        rows : int
            The number of rows in the plate.
        cols : int
            The number of columns in the plate.

        Attributes
        ----------
        rows : int
            Stores the number of rows in the plate.
        cols : int
            Stores the number of columns in the plate.
        data : numpy.ndarray
            A 2D array to hold data for each well in the plate.
            Each element is initialized as an empty object and can be
            filled with information related to substance, concentration, or other custom values.
        """
        self.rows = rows
        self.cols = cols
        self.data = np.empty((rows, cols), dtype=object)

    def pos_to_index(self, row: int, col: int) -> int:
        """Convert a row and column position to a linear index.

        Parameters
        ----------
        row : int
            Row index.
        col : int
            Column index.

        Returns
        -------
        int
            Linear index for the position.
        """
        return row * self.cols + col

    def index_to_pos(self, index: int) -> Tuple[int, int]:
        """Convert a linear index to row and column positions.

        Parameters
        ----------
        index : int
            Linear index.

        Returns
        -------
        tuple of int
            Row and column positions.
        """
        return divmod(index, self.cols)

    def convert_concentration(self, concentration: float) -> Tuple[float, str]:
        """Convert concentration to a more readable format (mM, µM, nM, pM).

        Parameters
        ----------
        concentration : float
            Concentration value in M.

        Returns
        -------
        tuple
            Display concentration and unit.
        """
        if concentration > 9 * 1e-3:
            unit = "mM"
            concentration_display = concentration
        elif concentration <= 9 * 1e-3 and concentration > 9 * 1e-6:
            unit = "µM"
            concentration_display = concentration * 1e3
        elif concentration <= 9 * 1e-6 and concentration > 9 * 1e-9:
            unit = "nM"
            concentration_display = concentration * 1e6
        else:
            unit = "pM"
            concentration_display = concentration * 1e9
        return concentration_display, unit

    def index_to_row_label(self, index: int) -> str:
        """Convert row index to a label (e.g., 'A', 'B').

        Parameters
        ----------
        index : int
            Row index.

        Returns
        -------
        str
            Row label.
        """
        label = ""
        index = self.rows - index - 1
        while index >= 0:
            label = chr(index % 26 + ord("A")) + label
            index = index // 26 - 1
        return label

    def fill_serial_dilutions(
        self,
        start_pos: str,
        initial_concentration: float,
        dilution_factor: float,
        num_dilutions: int,
        substance: str,
        color: str,
    ) -> None:
        """Fill the plate with serial dilutions starting from a given position.

        Parameters
        ----------
        start_pos : str
            Start position (e.g., 'A1').
        initial_concentration : float
            Initial concentration.
        dilution_factor : float
            Factor for serial dilutions.
        num_dilutions : int
            Number of dilutions.
        substance : str
            Name of the substance.
        color : str
            Color for the substance representation.
        """
        start_row = ord(start_pos[0]) - ord("A")
        start_col = int(start_pos[1:]) - 1
        start_idx = self.pos_to_index(start_row, start_col)

        for i in range(num_dilutions):
            concentration = initial_concentration / (dilution_factor**i)
            row, col = self.index_to_pos(start_idx + i)
            if row < self.rows and col < self.cols:
                concentration_display, unit = self.convert_concentration(concentration)
                self.data[row, col] = (
                    f"{chr(65+row)}{col+1}",
                    substance,
                    color,
                    concentration_display,
                    unit,
                )

    def fill_custom(self, pos: str, value: float, substance: str, color: str) -> None:
        """Fill a specific well with a custom value.

        Parameters
        ----------
        pos : str
            Well position (e.g., 'A1').
        value : float
            Custom value for the well.
        substance : str
            Substance name.
        color : str
            Color for the substance.
        """
        row = ord(pos[0]) - ord("A")
        col = int(pos[1:]) - 1
        if row < self.rows and col < self.cols:
            self.data[row, col] = (f"{chr(65+row)}{col+1}", substance, color, value, "")

    def __str__(self) -> str:
        """Return a string representation of the plate's contents.

        Iterates over each well in the plate and appends its contents to a string.
        If a well is empty, it appends "Empty" in its place.

        Returns
        -------
        str
            A formatted string where each row represents a row of wells in the plate,
            with each well displaying its contents or marked as "Empty" if it has no data.
        """
        result = ""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.data[row, col] is not None:
                    result += f"{self.data[row, col]} "
                else:
                    result += "Empty "
            result += "\n"
        return result

    def save(self, filename: str) -> str:
        """Save plate data to a file with a .star extension.

        Parameters
        ----------
        filename : str
            The base path to save the data. If the filename does not already
            end with `.star`, the function will automatically append it.

        Returns
        -------
        str
            The full path of the saved file, including the .star extension.

        Notes
        -----
        The saved file will have a `.star` extension if not already present,
        and the data will be stored in binary format using NumPy's `np.save`.
        """
        # Append `.star` extension if not already present
        if not filename.endswith(".star"):
            filename += ".star"

        with open(filename, "wb") as f:
            np.save(f, self.data)

        # Print confirmation message
        print(f"Data successfully saved to {filename}")

        return filename

    def plot_plate(
        self, figsize: Tuple[int, int] = (14, 8), show_concentration: bool = True
    ) -> None:
        """Plot the plate with well contents and concentrations.

        Parameters
        ----------
        figsize : tuple
            Figure size.
        show_concentration : bool
            Display concentration if True.
        """
        legend_elements = {}
        fig, ax = plt.subplots(figsize=figsize)
        for row in range(self.rows):
            for col in range(self.cols):
                if self.data[row, col] is not None:
                    well_name, substance, color, concentration, unit = self.data[
                        row, col
                    ]
                    circle = Circle(
                        (col + 0.5, self.rows - row - 0.5),
                        0.4,
                        edgecolor="black",
                        facecolor=color,
                    )
                    ax.add_patch(circle)

                    if show_concentration:
                        text = (
                            f"{concentration:.2f}{unit}"
                            if isinstance(concentration, (int, float))
                            else f"{concentration}{unit}"
                        )
                        ax.text(
                            col + 0.5,
                            self.rows - row - 0.5,
                            text,
                            ha="center",
                            va="center",
                            fontsize=10,
                            color="white" if color in ["black", "blue"] else "black",
                        )

                    if substance not in legend_elements:
                        legend_elements[substance] = Line2D(
                            [0],
                            [0],
                            marker="o",
                            color="w",
                            label=substance,
                            markersize=10,
                            markerfacecolor=color,
                            markeredgecolor="black",
                        )
                else:
                    circle = Circle(
                        (col + 0.5, self.rows - row - 0.5),
                        0.4,
                        fill=False,
                        edgecolor="black",
                    )
                    ax.add_patch(circle)

        ax.set_xlim(0, self.cols)
        ax.set_ylim(0, self.rows)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticks(np.arange(self.cols) + 0.5)
        ax.set_xticklabels(np.arange(1, self.cols + 1))
        ax.set_yticks(np.arange(self.rows) + 0.5)
        labels = [self.index_to_row_label(i) for i in range(self.rows)]
        ax.set_yticklabels(labels, fontsize=6)
        ax.set_aspect("equal")
        ax.legend(
            handles=legend_elements.values(), loc="upper left", bbox_to_anchor=(1, 1)
        )
        plt.show()

    def generate_gcode(
        self,
        x_spacing: float = 9,
        y_spacing: float = 9,
        z_safe: float = 0,
        z_read: float = 0,
        offset: float = -90,
        filename: Optional[str] = None,
    ) -> str:
        """Generate G-code for CNC movement across wells.

        Parameters
        ----------
        x_spacing : float
            X-axis spacing between wells in mm.
        y_spacing : float
            Y-axis spacing between wells in mm.
        z_safe : float
            Safe height in Z-axis for non-reading positions.
        z_read : float
            Reading height in Z-axis.
        offset : float
            Offset for Y-axis.
        filename : str, optional
            File path to save the G-code.
        """
        gcode = []
        gcode.append("G21; Set units to millimeters")
        gcode.append("G90; Use absolute positioning")

        for row in range(self.rows):
            for col in range(self.cols):
                if self.data[row, col] is not None:
                    x = col * x_spacing
                    y = (row * y_spacing) + offset
                    gcode.append(
                        f"G0 X{x:.2f} Y{y:.2f} Z{z_safe:.2f}"
                        f"; Move to above well at ({row}, {col})"
                    )
                    gcode.append(f"G0 Z{-z_read:.2f} ; Lower to reading height")
                    gcode.append(f"Read well at {chr(ord('A') + row)}{col+1}")
                    gcode.append(f"G0 Z{z_safe:.2f} ; Raise back to safe height")

        gcode.append("G0 X0 Y0; Return")
        gcode.append("M30 ; End of program")
        gcode_str = "\n".join(gcode)

        if filename is not None:
            with open(filename, "w") as file:
                file.write(gcode_str)

        return gcode_str


def load_plate(filename: str) -> Plate:
    """Load plate data from a file.

    Parameters
    ----------
    filename : str
        File path from which to load the data.

    Returns
    -------
    Plate
        Plate object with loaded data.
    """
    with open(filename, "rb") as f:
        data = np.load(f, allow_pickle=True)
        rows, cols = data.shape
        plate = Plate(rows, cols)
        plate.data = data
        return plate
