# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

import python_workflow
import sphinx_rtd_theme


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'python-workflow'
copyright = '2024, Anthony K GROSS'
author = 'Anthony K GROSS'

version = python_workflow.get_version()

pygments_style = "sphinx"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 5,
}

# https://www.sphinx-doc.org/fr/master/usage/extensions/autodoc.html
autodoc_default_options = {
    'members': True,
    'inherited-members': False,
    'show-inheritance': True,
    'special-members': '__init__'
}

html_context = {
    "display_github": True,
    "github_user": "anthonykgross",
    "github_repo": "python-workflow",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}
