# cuckoo-api
A Python library to interface with a Cuckoo instance

This library interfaces with the Cuckoo malware sandbox at:

http://www.cuckoosandbox.org

This library can be used either with the
api.py script in utils.

# Installation:

```
pip install git+https://github.com/keithjjones/cuckoo-api.git
```
...or...
```
pip install cuckoo-api
```

# Usage:
You can load this module like any other module.  As an example to submit a sample to Cuckoo:
```
Python 2.7.12 (v2.7.12:d33e0cf91556, Jun 27 2016, 15:24:40) [MSC v.1500 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import CuckooAPI
>>> api = CuckooAPI.CuckooAPI("10.0.0.144", APIPY=True, port=8090)
>>> api.submitfile("malware.exe")
```

# Documentation

Online documentation: Coming Soon!

Documentation can be built from the docs directory.  For example, go into that directory
and type make html.  

# Resources:

Documentation can be found at the following links:

  - API:
  	- https://downloads.cuckoosandbox.org/docs/usage/api.html
  - Setup information:
  	- http://stackoverflow.com/questions/14399534/how-can-i-reference-requirements-txt-for-the-install-requires-kwarg-in-setuptool
  	- http://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/creation.html
    - https://pythonhosted.org/an_example_pypi_project/setuptools.html

# License:

This application is covered by the Creative Commons BY-SA license.

- https://creativecommons.org/licenses/by-sa/4.0/
- https://creativecommons.org/licenses/by-sa/4.0/legalcode

# Contributing:

If you would like to contribute you can fork this repository, make your changes, and
then send me a pull request to my "devel" branch.

# To Do:
  - Add memory API calls
