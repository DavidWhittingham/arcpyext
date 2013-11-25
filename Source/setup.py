import arcpyext

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    "arcpyext",
    "arcpyext.data",
    "arcpyext.exceptions",
    "arcpyext.mapping"
]

setup(
    name = "arcpyext",
    version = arcpyext.__version__,
    packages = packages,
    
    #misc files to include
    package_data = {
        "": ["LICENSE"]
    },
    
    #PyPI MetaData
    author = arcpyext.__author__,
    description = "Extended functionality for Esri's ArcPy site-package",
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
    
    zip_safe = True
)