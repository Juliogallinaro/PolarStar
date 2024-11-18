"""Module for controlling CNC machines in the POLARSTAR platform.

This module provides a `CNCController` class to manage communication with
CNC machines via serial connections, send G-code commands, and handle
callbacks for specific commands.

Classes:
    CNCController: Manages CNC machine communication and G-code execution.
"""

import time

import serial


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

    def register_callback(self, command, callback, *args, **kwargs):
        """Registers a callback for a specific G-code command.

        A callback is a function that gets executed whenever the specified
        G-code command is encountered during execution. Additional arguments
        can be passed to the callback.

        Args:
            command (str): The G-code command to monitor (e.g., 'G1').
            callback (callable): The function to call when the command is detected.
            args: Additional positional arguments to pass to the callback.
            kwargs: Additional keyword arguments to pass to the callback.

        """
        self.callbacks[command.lower()] = (callback, args, kwargs)

    def wait_for_idle(self, cnc_serial):
        """Waits until the CNC machine enters the 'Idle' state.

        Sends periodic status requests ("?") to the CNC machine and monitors
        the response until the machine reports the 'Idle' state.

        Args:
            cnc_serial (serial.Serial): The active serial connection to the CNC machine.
        """
        while True:
            cnc_serial.write(b"?")  # Request CNC status
            response = cnc_serial.readline().decode().strip()
            print(f"CNC Status: {response}")

            if "<Idle" in response:
                break
            time.sleep(0.1)

    def send_gcode(self, gcode_str):
        """Sends a series of G-code commands to the CNC machine.

        Each line of the G-code string is sent to the machine, and the response
        is monitored for confirmation ("ok"). If a callback is registered for
        a specific command, it will be executed before sending that command.

        Args:
            gcode_str (str): A multiline string containing G-code commands.

        Raises:
            Exception: If there is an error in serial communication.
        """
        try:
            # Establish serial communication
            cnc_serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # Wait for the connection to stabilize

            cnc_serial.flushInput()  # Clear input buffer

            for line in gcode_str.split("\n"):
                command = line.split()[0].lower() if line.strip() else None

                # Execute callback if registered for the command
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
            # Ensure the connection is closed
            time.sleep(1)
            cnc_serial.close()
            print("CNC connection closed.")
