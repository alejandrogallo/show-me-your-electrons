
from smye import * 

def printv(smth):
    if VERBOSE:
        print(smth)

LOGO = """
 ____  _  _  _  _  ____ 
/ ___)( \/ )( \/ )(  __)
\___ \/ \/ \ )  /  ) _) 
(____/\_)(_/(__/  (____)

"""

SETUP_INFO = dict(
    name             = "Show me your electrons",
    version          = "0.1.1",
    description      = "A little tool to parse electronic configurations",
    url              = "http://github.com/alejandrogallo/smye",
    author           = "Alejandro Gallo",
    license          = "MIT",
    packages         = ["smye"],
    install_requires = [],
    test_suite       = "smye.tests",
    scripts          = ["bin/smye"],
    zip_safe         = False)
