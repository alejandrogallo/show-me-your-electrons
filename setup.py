from setuptools import setup

setup(name="Show me your electrons",
    version="0.0.1",
    description="A little program to view VASP's OUTCAR electronic positions",
    url="http://github.com/alejandrogallo/smye",
    author="Alejandro Gallo",
    license="MIT",
    packages=["smye"],
    test_suite="smye.tests",
    scripts=["bin/show-me-your-electrons"],
    zip_safe=False)
