"""Scientific Tools for Automation and Replication - STAR.

STAR is a Python library focused on simplifying the automation of scientific experiments,
including data collection and hardware control. While STAR is designed to integrate with POLAR,
it can also be used independently for various scientific applications.

Modules:
- cnc: Manages CNC hardware communication and G-code operations.
- plate: Defines the Plate class for data management and optical measurement automation.

Exports:
- Plate: Represents a microplate for organizing and managing well-based data.
- load_plate: Loads a saved plate configuration from a file.
- CNCController: Handles CNC hardware control and communication.
"""

from .cnc import CNCController
from .plate import Plate
from .plate import load_plate


__all__ = ["Plate", "load_plate", "CNCController"]
