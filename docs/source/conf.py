# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Add path to source files for autodoc/napoleon ---------------------------

import os
import sys
sys.path.insert(0, os.path.abspath('../../src/dystrack'))


# -- Remove module docstrings ------------------------------------------------
# These are a holdover from the spyder days. They do not look good in the docs.

def remove_module_docstring(app, what, name, obj, options, lines):
    if what == "module":# and name == "dystrack":
        del lines[:]

def setup(app):
    app.connect("autodoc-process-docstring", remove_module_docstring)


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DySTrack'
copyright = '2025, Jonas Hartmann, Zimeng Wu'
author = 'Jonas Hartmann, Zimeng Wu'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon'
]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

html_context = {
   "default_mode" : "dark"  # Set the default style to dark
}

html_sidebars = {
    #"index" : ["sidebar-nav-bs.html"],
    #"usage" : ["sidebar-nav-bs.html"],
    "api" : []  # Remove primary (left) sidebar from API reference pages
}

html_theme_options = {
  "secondary_sidebar_items": [],
  "logo": {
    "alt_text": "DySTrack - Home",
    "image_light": "images/logos/DySTrack_logo_lite.svg",
    "image_dark": "images/logos/DySTrack_logo_dark.svg"
    }
}