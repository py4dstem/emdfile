# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

import emdfile

# Project Info
project = 'emdfile'
copyright = '2024, Benjamin H. Savitzky'
author = 'Benjamin H. Savitzky'
release = emdfile.__version__

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

# Globs
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Configure Theme
html_static_path = ['_static']
html_theme = 'alabaster'
html_theme_options = {
    'description' : 'An HDF5/Python interface',
    'fixed_sidebar' : 'true',
    'sidebar_collapse' : 'true',
    'show_relbar_bottom' : 'true',
    'github_banner' : 'true',
    'github_button' : 'true',
    'github_user' : 'py4dstem',
    'github_repo' : 'emdfile',
}
html_sidebars = {
    '**' : [
        'about.html',
        'localtoc.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}

# Configure napolean
napoleon_numpy_docstring = True
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_use_admonition_for_examples = True  # TODO toggle this



