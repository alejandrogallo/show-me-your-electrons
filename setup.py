from setuptools import setup

setup(name           = "Show me your electrons",
    version          = "0.0.1",
    description      = "A little program to view VASP's OUTCAR electronic positions",
    url              = "http://github.com/alejandrogallo/smye",
    author           = "Alejandro Gallo",
    license          = "MIT",
    packages         = ["smye"],
    install_requires = [],
    test_suite       = "smye.tests",
    scripts          = ["bin/smye"],
    zip_safe         = False)
