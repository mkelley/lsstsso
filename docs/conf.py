# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "LSST SSO Tools"
copyright = "2026, Michael S. P. Kelley"
author = "Michael S. P. Kelley"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "pytest_doctestplus.sphinx.doctestplus",
    "sphinx_automodapi.automodapi",
    "sphinx.ext.intersphinx",
]
numpydoc_show_class_members = False

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_resolve_self = "lsstsso"
intersphinx_mapping = {
    "astropy": ("https://docs.astropy.org/en/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "sbpy": ("https://sbpy.readthedocs.io/en/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

global_substitutions: dict[str, str] = {
    # NumPy
    "ndarray": ":class:`numpy.ndarray`",
    # Table
    "Column": ":class:`~astropy.table.Column`",
    "MaskedColumn": ":class:`~astropy.table.MaskedColumn`",
    "TableColumns": ":class:`~astropy.table.TableColumns`",
    "Row": ":class:`~astropy.table.Row`",
    "Table": ":class:`~astropy.table.Table`",
    "QTable": ":class:`~astropy.table.QTable`",
    # Time
    "Time": ":class:`~astropy.time.Time`",
    "TimeDelta": ":class:`~astropy.time.TimeDelta`",
    # Units
    "PhysicalType": ":class:`~astropy.units.PhysicalType`",
    "Quantity": ":class:`~astropy.units.Quantity`",
    "Unit": ":class:`~astropy.units.UnitBase`",
    "StructuredUnit": ":class:`~astropy.units.StructuredUnit`",
}

links_to_become_substitutions: dict[str, str] = {
    # Python
    "Python": "https://www.python.org",
    "PEP8": "https://www.python.org/dev/peps/pep-0008",
    # NumPy
    "NumPy": "https://numpy.org",
    "numpydoc": "https://pypi.org/project/numpydoc",
    # matplotlib
    "Matplotlib": "https://matplotlib.org",
    # scipy
    "SciPy": "https://www.scipy.org",
    # IPython
    "IPython": "https://ipython.org",
    # pip
    "pip": "https://pip.pypa.io",
    # pytest
    "pytest": "https://pytest.org/en/latest/index.html",
    "pytest-doctestplus": "https://github.com/astropy/pytest-doctestplus",
    "pytest-remotedata": "https://github.com/astropy/pytest-remotedata",
}

processed_links = {
    key: f"`{key} <{value}>`_" for key, value in links_to_become_substitutions.items()
}

global_substitutions |= processed_links
