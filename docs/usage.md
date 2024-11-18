```{eval-rst}
Usage
=====

.. currentmodule:: polarstar

.. _installation:

Installation
------------

To use Polar Star, first install it using pip:

.. code-block:: console

   pip install polarstar



Creating and Configuring a Plate
--------------------------------

To create a plate and manage it, you can use the ``Plate`` class.

.. autoclass:: Plate
   :no-members:

Creating a Plate
----------------

To initialize a plate with a specific number of rows and columns:

.. code-block:: python

   # Create a plate with 8 rows and 12 columns
   plate = Plate(rows=8, cols=12)

Filling Wells with Serial Dilutions
-----------------------------------

To fill wells with a series of dilutions, you can use the ``fill_serial_dilutions`` method. This will add a serial dilution across a specified range of wells, starting from an initial concentration.

.. automethod:: Plate.fill_serial_dilutions


Example:

.. code-block:: python

   # Fill serial dilutions starting from position A1
   plate.fill_serial_dilutions(
       start_pos="A1",
       initial_concentration=10e-3,  # 0.01 mM
       dilution_factor=2,
       num_dilutions=8,
       substance="Substance X",
       color="blue"
   )

Plotting the Plate
------------------

To visualize the contents of the plate, including well positions, concentrations, and colors, use the ``plot_plate`` method.

.. automethod:: Plate.plot_plate

Example:

.. code-block:: python

   # Plot the plate
   plate.plot_plate(figsize=(12, 8), show_concentration=True)

Output:

.. image:: images/plate_visualization_1.png
   :alt: Visualization of the plate
   :align: center
   :width: 90%

Adding Custom Values to Wells
-----------------------------

To add a custom value to a specific well, use the ``fill_custom`` method.

.. automethod:: Plate.fill_custom

Parameters:

- ``pos``: Position of the well (e.g., `"B1"`).
- ``value``: Custom value.
- ``substance``: Substance name.
- ``color``: Color for representation.

Example usage:

.. code-block:: python

   # Add a custom value in position B1
   plate.fill_custom(pos="B1", value="Blank", substance="Substance Y", color="green")

Plot the plate to visualize the custom value:

.. code-block:: python

   # Plot the plate
   plate.plot_plate(figsize=(12, 8), show_concentration=True)

Output:

.. image:: images/plate_visualization_2.png
   :alt: Visualization of the plate
   :align: center
   :width: 90%


Saving and Loading Plates
-------------------------

To save or load a plate’s state to and from a `.star` file, use ``save`` and the standalone ``load_plate`` function, respectively.

.. automethod:: Plate.save
.. autofunction:: load_plate

For example:

.. code-block:: python

   # Save the plate state to 'my_plate.star'
   plate.save('my_plate')

   # Load a plate from the file 'my_plate.star'
   loaded_plate = load_plate('my_plate.star')


Generating G-code for CNC Control
---------------------------------

To generate G-code for automated CNC control over the wells in the plate, use the ``generate_gcode`` method.

.. automethod:: Plate.generate_gcode

Example:

.. code-block:: python

   # Generate G-code for plate wells with specific parameters
   plate.generate_gcode(
      x_spacing=32,       # Distance between wells along the X-axis (e.g., 32 mm)
      y_spacing=28.7,     # Distance between wells along the Y-axis (e.g., 28.7 mm)
      z_read=0,           # Z-axis height for interaction (e.g., surface level)
      offset=-80,         # Calibration offset
      filename="plate.g"  # Output G-code file
   )


Expected Output:
The file plate.g will contain G-code commands similar to:

.. code-block::

   G21; Set units to millimeters
   G90; Use absolute positioning
   G0 X0.00 Y-80.00 Z0.00; Move to above well at (0, 0)
   G0 Z0.00; Lower to reading height
   Read well at A1
   G0 Z0.00; Raise back to safe height
   G0 X32.00 Y-80.00 Z0.00; Move to above well at (0, 1)
   G0 Z0.00; Lower to reading height
   Read well at A2
   G0 Z0.00; Raise back to safe height
   G0 X64.00 Y-80.00 Z0.00; Move to above well at (0, 2)
   G0 Z0.00; Lower to reading height
   Read well at A3
   G0 Z0.00; Raise back to safe height
   G0 X96.00 Y-80.00 Z0.00; Move to above well at (0, 3)
   G0 Z0.00; Lower to reading height
   ...
```
