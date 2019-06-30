from setuptools import setup, find_packages

with open('arcpyext/_version.py') as fin: exec(fin.read(), globals())
with open('requirements.txt') as fin: requirements=[s.strip() for s in fin.readlines()]
with open('readme.rst') as fin: long_description = fin.read()

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

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
    long_description_content_type = "text/x-rst",
    license = "BSD 3-Clause",
    keywords = "arcgis esri arcpy",
    url = "https://github.com/DavidWhittingham/arcpyext",
    classifiers = (
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python"
    ),

    zip_safe = False
)
