"""Module for controlling CNC machines in the POLARSTAR platform.

This module provides a `CNCController` class to manage communication with
CNC machines via serial connections, send G-code commands, and handle
callbacks for specific commands.

Classes:
    CNCController: Manages CNC machine communication and G-code execution.
"""

import os
import time
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import serial
from IPython.display import HTML
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import art3d

from .plate import Plate


def create_circle_points(
    center: List[float], radius: float, num_points: int = 50
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create points for drawing a circle in 3D.

    Parameters
    ----------
    center : list of float
        Center coordinates [x, y, z].
    radius : float
        Circle radius.
    num_points : int, optional
        Number of points to create the circle, by default 50.

    Returns
    -------
    tuple of numpy.ndarray
        X, Y, Z coordinates of the circle points.
    """
    theta = np.linspace(0, 2 * np.pi, num_points)
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    z = np.full_like(theta, center[2])
    return x, y, z


class CNCController:
    """A controller for managing CNC machines via serial communication.

    This class provides functionality to send G-code commands to CNC machines,
    monitor their status, and register callbacks for specific G-code commands.

    Attributes:
        port (str): The serial port to which the CNC machine is connected.
        baudrate (int): The communication speed in bits per second.
        timeout (int): The timeout for serial read operations, in seconds.
        callbacks (dict): A dictionary of registered callbacks for G-code commands.
    """

    def __init__(self, port="COM6", baudrate=115200, timeout=1):
        """Initializes the CNCController with the specified parameters.

        Args:
            port (str): The serial port for communication (default: 'COM6').
            baudrate (int): The communication speed in bps (default: 115200).
            timeout (int): The timeout for serial read operations, in seconds (default: 1).
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.callbacks = {}

    def register_callback(
        self, command: str, callback: Callable, *args: Any, **kwargs: Any
    ) -> None:
        """Register a callback for a specific G-code command.

        Parameters
        ----------
        command : str
            The G-code command to monitor (e.g., 'G1').
        callback : callable
            The function to call when the command is detected.
        args : Any
            Additional positional arguments to pass to the callback.
        kwargs : Any
            Additional keyword arguments to pass to the callback.
        """
        self.callbacks[command.lower()] = (callback, args, kwargs)

    def wait_for_idle(self, cnc_serial: serial.Serial) -> None:
        """Wait until the CNC machine enters the 'Idle' state.

        Parameters
        ----------
        cnc_serial : serial.Serial
            The active serial connection to the CNC machine.
        """
        while True:
            cnc_serial.write(b"?")  # Request CNC status
            response = cnc_serial.readline().decode().strip()
            print(f"CNC Status: {response}")

            if "<Idle" in response:
                break
            time.sleep(0.1)

    def _parse_gcode_input(self, input_data: Optional[Union["Plate", str]]) -> str:
        """Parse input data into G-code string.

        Parameters
        ----------
        input_data : Plate, str, or file path
            Can be:
            - A `Plate` object (generates G-code automatically).
            - A string containing G-code.
            - A file path to a G-code file.

        Returns
        -------
        str
            The parsed G-code string.

        Raises
        ------
        ValueError
            If input_data is None or invalid.
        """
        if input_data is None:
            raise ValueError(
                "A Plate object, G-code string, or file path must be provided."
            )

        # Type checking before processing
        if not isinstance(input_data, (Plate, str)):
            raise ValueError(
                "Invalid input type. Must be a Plate object, G-code string, or file path."
            )

        # If input is a Plate object, generate G-code
        if isinstance(input_data, Plate):
            return input_data.generate_gcode()

        # If input is a string, check if it's a file path
        if os.path.isfile(input_data):
            with open(input_data) as f:
                return f.read()

        # Otherwise, treat it as direct G-code
        return input_data

    def send_gcode(self, input_data: Optional[Union["Plate", str]] = None) -> None:
        """Send G-code commands to the CNC machine.

        Parameters
        ----------
        input_data : Plate, str, or file path
            Can be:
            - A `Plate` object (generates G-code automatically).
            - A string containing G-code.
            - A file path to a G-code file.

        Raises
        ------
        ValueError
            If `input_data` is None or invalid.
        Exception
            If there is an error in serial communication.
        """
        try:
            gcode_str = self._parse_gcode_input(input_data)

            # Establish serial communication
            cnc_serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # Wait for connection stabilization
            cnc_serial.flushInput()  # Clear input buffer

            for line in gcode_str.split("\n"):
                command = line.split()[0].lower() if line.strip() else None

                # Execute callback if registered
                if command and command in self.callbacks:
                    callback, args, kwargs = self.callbacks[command]
                    self.wait_for_idle(cnc_serial)
                    time.sleep(0.1)
                    callback(line, *args, **kwargs)
                    continue

                # Send G-code line to CNC
                if line.strip():
                    cnc_serial.write((line + "\n").encode())
                    print(f"Sent: {line}")

                    # Wait for "ok" response
                    response = cnc_serial.readline().decode().strip()
                    while "ok" not in response.lower():
                        response = cnc_serial.readline().decode().strip()
                        if response:
                            print(f"CNC Response: {response}")
                    print(f"CNC confirmed 'OK' for: {line}")
                    time.sleep(0.1)

        except Exception as e:
            print(f"Error communicating with CNC: {e}")
            raise
        finally:
            if "cnc_serial" in locals():
                time.sleep(1)
                cnc_serial.close()
                print("CNC connection closed.")

    def _parse_gcode_positions(self, plate) -> np.ndarray:
        """Parse G-code and extract positions for 3D simulation.

        Parameters
        ----------
        plate : Plate
            The plate object to visualize.

        Returns
        -------
        np.ndarray
            Array of positions (x, y, z).
        """
        positions: List[Tuple[float, float, float]] = [
            (0.0, 0.0, 0.0)
        ]  # Changed to float tuple
        current_pos = {"X": 0.0, "Y": 0.0, "Z": 0.0}

        gcode = plate.generate_gcode()
        lines = gcode.split("\n")

        for line in lines:
            line = line.split(";")[0].strip()  # Remove comments
            if not line or line.startswith(";"):
                continue

            words = line.split()
            if not words or words[0] not in ["G0", "G1"]:
                continue

            new_pos = current_pos.copy()
            for word in words[1:]:
                if word[0] in ["X", "Y", "Z"]:
                    try:
                        value = float(word[1:])
                        if word[0] == "X":
                            value = -value
                        elif word[0] == "Z":
                            value = -value
                        new_pos[word[0]] = value
                    except ValueError:
                        continue

            positions.append((new_pos["X"], new_pos["Y"], new_pos["Z"]))
            current_pos = new_pos

        return np.array(positions)

    def simulate(self, plate, figsize: Tuple[int, int] = (15, 10)) -> HTML:
        """Create a 3D simulation of the G-code path.

        Parameters
        ----------
        plate : Plate
            The plate object to visualize.
        figsize : tuple of int, optional
            Figure size (width, height), by default (15, 10).

        Returns
        -------
        IPython.display.HTML
            HTML animation of the 3D simulation.
        """
        positions = self._parse_gcode_positions(plate)

        # Create figure and axis
        fig = plt.figure(figsize=figsize, constrained_layout=True)
        ax = fig.add_subplot(111, projection="3d")
        radius = plate.diameter / 2

        # Plot wells
        for col in range(plate.cols):
            for row in range(plate.rows):
                center = [
                    -col * plate.x_spacing,
                    row * plate.y_spacing + plate.offset_y,
                    plate.offset_z,
                ]
                x, y, z = create_circle_points(center, radius)

                if plate.data[row, col] is not None:
                    _, _, color, _, _ = plate.data[row, col]
                    ax.plot(x, y, z, color="black", linewidth=1)
                    verts = list(zip(x, y, z))

                    art3d_poly = art3d.Poly3DCollection([verts])
                    art3d_poly.set_color(color)
                    art3d_poly.set_alpha(0.5)
                    ax.add_collection3d(art3d_poly)
                else:
                    ax.plot(x, y, z, "k-", alpha=0.3)

        # Calculate plot bounds
        x_min = -((plate.cols - 1) * plate.x_spacing + radius)
        x_max = radius
        y_min = -radius + plate.offset_y
        y_max = ((plate.rows - 1) * plate.y_spacing + radius) + plate.offset_y
        z_min = -radius + plate.offset_z
        z_max = radius + plate.offset_z

        if positions.size:
            x_min = min(x_min, positions[:, 0].min() - radius)
            x_max = max(x_max, positions[:, 0].max() + radius)
            y_min = min(y_min, positions[:, 1].min() - radius)
            y_max = max(y_max, positions[:, 1].max() + radius)
            z_min = min(z_min, positions[:, 2].min() - radius)
            z_max = max(z_max, positions[:, 2].max() + radius)

        # Add margins
        x_range = x_max - x_min
        y_range = y_max - y_min
        z_range = z_max - z_min
        margin_x = x_range * 0.1
        margin_y = y_range * 0.1
        margin_z = z_range * 0.1

        # Set plot limits and labels
        ax.set_xlim(x_min - margin_x, x_max + margin_x)
        ax.set_ylim(y_min - margin_y, y_max + margin_y)
        ax.set_zlim(z_min - margin_z, z_max + margin_z)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("3D Simulation of the G-code path")
        ax.set_aspect("equal")
        ax.set_zticks(np.linspace(np.floor(z_min), np.ceil(z_max), 4, dtype=int))

        # Animation
        if not positions.size:
            # If there are no positions, return a static plot
            plt.close()
            return HTML(fig.canvas.to_html5_fmt())

        (line,) = ax.plot([], [], [], "r-", linewidth=2)
        (point,) = ax.plot([], [], [], "ro", markersize=8)

        def update(frame):
            line.set_data(positions[: frame + 1, 0], positions[: frame + 1, 1])
            line.set_3d_properties(positions[: frame + 1, 2])
            point.set_data([positions[frame, 0]], [positions[frame, 1]])
            point.set_3d_properties([positions[frame, 2]])
            return line, point

        anim = FuncAnimation(
            fig, update, frames=len(positions), interval=100, blit=True
        )

        plt.close()
        return HTML(anim.to_jshtml())
