from ez_setup import use_setuptools
use_setuptools()
    
import arcpyext

from setuptools import setup, find_packages

setup(
    name = "arcpyext",
    version = arcpyext.__version__,
    packages = find_packages(),
    
    #misc files to include
    package_data = {
        "": ["LICENSE"]
    },
    
    #PyPI MetaData
    author = arcpyext.__author__,
    description = "Extended functionality for Esri's ArcPy site-package",
    license = "BSD 3-Clause",
    keywords = "arcgis esri arcpy",
    url = "https://github.com/DavidWhittingham/agstools",
    classifiers=(
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7"
    ),
    
    zip_safe = True
)