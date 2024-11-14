"""Polar Star.

STAR is a Python library focused on simplifying the automation of scientific experiments,
including data collection and hardware control. While STAR is designed to integrate with POLAR,
it can also be used independently for various scientific applications.

Modules:
- plate: Defines the Plate class for handling data and automating optical measurements.

Exports:
- Plate: Main class representing a plate.
- load_plate: Function to load a saved plate configuration from a file.
"""

from .plate import Plate
from .plate import load_plate


__all__ = ["Plate", "load_plate"]
