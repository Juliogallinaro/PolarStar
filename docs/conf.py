"""Sphinx configuration."""
project = "Polar Star"
author = "Júlio Gallinaro Maranho and Patrícia Aparecida da Ana"
copyright = "2024, Júlio Gallinaro Maranho and Patrícia Aparecida da Ana"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
