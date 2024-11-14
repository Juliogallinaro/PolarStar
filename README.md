# Polar Star

[![PyPI](https://img.shields.io/pypi/v/polarstar.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/polarstar.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/polarstar)][python version]
[![License](https://img.shields.io/pypi/l/polarstar)][license]

[![Documentation Status](https://readthedocs.org/projects/polarstar/badge/?version=latest)](https://polarstar.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/juliogallinaro/PolarStar/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/juliogallinaro/PolarStar/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/PolarStar/
[status]: https://pypi.org/project/PolarStar/
[python version]: https://pypi.org/project/PolarStar
[read the docs]: https://PolarStar.readthedocs.io/
[tests]: https://github.com/juliogallinaro/PolarStar/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/juliogallinaro/PolarStar
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Overview

**POLAR** (Platform for Optical Laboratory Automation and Research) and **STAR** (Scientific Tools for Automation and Research) are designed to facilitate the automation and control of experiments in scientific research, with a special focus on optical experiments.

- **POLAR** is a hardware platform that enables precise control and automation in optical laboratories, supporting high-throughput experimentation and analysis.
- **STAR** is a Python library that provides tools for automation, data collection, and analysis, designed to work seamlessly with POLAR or as a standalone solution for general scientific research.

## POLAR: Platform for Optical Laboratory Automation and Research

**POLAR** is a modular hardware platform created for automating optical experiments, providing researchers with control over spectrometers, sensors, and other lab equipment. It supports precise positioning and integration of various optical instruments, making it ideal for high-throughput spectroscopy, photonics, and related experiments.

### Key Features

- **Precision Positioning**: Integrates with CNC systems to allow for precise control of sample positioning.
- **Optical Experimentation**: Compatible with multiple optical sensors and devices, such as spectrometers and light sources.
- **Modular Design**: Easily integrates with a wide range of optical devices and equipment.
- **Automation Support**: Enables automated, high-throughput experimental setups.

### Getting Started with POLAR

To use POLAR, you can set up the equipment and connect it to STAR for data collection and control.

---

## STAR: Scientific Tools for Automation and Research

**STAR** is a Python library focused on simplifying the automation of scientific experiments, including data collection and hardware control. While STAR is designed to integrate with POLAR, it can also be used independently for various scientific applications.

## Features

- **Automated Data Collection**: Simplifies gathering and processing data from different lab instruments.
- **Hardware Control**: Provides interfaces to control lab equipment, including spectrometers and CNC machines.
- **Scalable and Modular**: STAR’s design supports multiple scientific disciplines beyond optical experiments.

## Requirements

- Python 3.8 or newer
- Additional dependencies listed in [pyproject.toml](https://github.com/juliogallinaro/polarstar/blob/main/pyproject.toml)

## Installation

You can install _Polar Star_ via [pip] from [PyPI]:

```console
$ pip install polarstar
```

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [GPL 3.0 license][license],
_Polar Star_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/juliogallinaro/PolarStar/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/juliogallinaro/PolarStar/blob/main/LICENSE
[contributor guide]: https://github.com/juliogallinaro/PolarStar/blob/main/CONTRIBUTING.md
[command-line reference]: https://PolarStar.readthedocs.io/en/latest/usage.html
