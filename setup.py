try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('arcpyext/_version.py') as fin: exec(fin)
with open('requirements.txt') as fin: requirements=[s.strip() for s in fin.readlines()]
with open('readme.rst') as fin: long_description = fin.read()

packages = [
    "arcpyext",
    "arcpyext.conversion",
    "arcpyext.data",
    "arcpyext.exceptions",
    "arcpyext.mapping",
    "arcpyext.publishing",
    "arcpyext.toolbox"
]

setup(
    name = "arcpyext",
    version = __version__,
    packages = packages,

    #dependencies
    install_requires = requirements,

    #misc files to include
    package_data = {
        "": ["LICENSE"]
    },

    #PyPI MetaData
    author = __author__,
    description = "Extended functionality for Esri's ArcPy site-package",
    long_description = long_description,
    license = "BSD 3-Clause",
    keywords = "arcgis esri arcpy",
    url = "https://github.com/DavidWhittingham/arcpyext",
    classifiers = (
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7"
    ),

    zip_safe = False
)
