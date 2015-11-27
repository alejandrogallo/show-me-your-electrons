import os, sys

VERBOSE=True

class Diagram(object):
    def __init__(self, filePath, verbose=VERBOSE):
        self.filePath = filePath
        self.verbose = VERBOSE
    def vprint(self, something, err=False):
        if self.verbose:
            if not err :
                print("Diagram:: %s"%something)
            else:
                print("Diagram::ERROR:: %s"%something)
    def parseFile(self):
        """ This function parses the electronic configuration of the filePath """
        try:
            self.vprint("Trying to open file %s"%self.filePath)
            fd = open(self.filePath,"r")
        except IOError, e:
            self.vprint("File %s could not be opened"%self.filePath, True)
            raise IOError(e)
        else:
            self.vprint("Reading file")
            

