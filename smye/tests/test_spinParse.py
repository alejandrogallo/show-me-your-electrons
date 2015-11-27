import smye 


import unittest


class TestSpinOutcar(unittest.TestCase):
    def setUp(self):
        self.diagram = smye.Diagram(filePath="OUTCAR")
        self.diagram._parseFile()
    def tearDown(self):
        pass
    def test_parse(self):
        self.diagram._parseFile()
    def test_showASCII(self):
        self.diagram.showASCII()
