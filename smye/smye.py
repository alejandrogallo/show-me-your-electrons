import os, sys

VERBOSE=True

class Diagram(object):
    def __init__(self, filePath, verbose=VERBOSE, spin=True):
        self.filePath = filePath
        self.verbose = VERBOSE
        self.spin = spin
        self.spinOccupation=False
    def vprint(self, something, err=False):
        if self.verbose:
            if not err :
                print("Diagram:: %s"%something)
            else:
                raise Exception("Diagram::ERROR:: %s"%something)
    def _parseFile(self):
        """ This function parses the electronic configuration of the filePath """
        try:
            self.vprint("Trying to open file %s"%self.filePath)
            fd = open(self.filePath,"r")
        except IOError, e:
            self.vprint("File %s could not be opened"%self.filePath, True)
            raise IOError(e)
        else:
            self.vprint("Reading file")
            fileBuffer = fd.read()
            if self.spin:
                return self._parseSpin(fileBuffer)
    def _parseSpin(self, fileBuffer):
        self.spinOccupation = {"1":[], "2":[]}
        separator = {"1":"spin component 2", "2":"-----"}
        for spin in ["1","2"]:
            self.vprint("Parsing information for spin %s"%spin)
            # The separators tell you up until which characters the spin part goes
            # For spin component 1, the information goes until the text spin component 2 is found
            # For spin component 2, the information goes until the ------ line is found 
            spinBuffer = fileBuffer.split("spin component %s"%spin)
            if len(spinBuffer)==1:
                self.vprint("There is no 'spin component %s' part in file %s"%(spin, self.filePath), True)
                sys.exit(-1)
            else:
                lastSpinBuffer = spinBuffer[-1]
                lastSpinBufferCleaned = lastSpinBuffer.split(separator[spin])
                if len(lastSpinBufferCleaned)==1:    
                    self.vprint("There was a problem parsing the information for spin %s"%(spin), True)
                else:
                    self.spinOccupation[spin]=self._parseElectronicConfiguration(lastSpinBufferCleaned[0])
                    #print self.spinOccupation[spin]
        return self.spinOccupation
    def _parseElectronicConfiguration(self, string):
        """ 
            This function parses the electronic configuration from a string (fileBuffer)
            The format of the string should be a table with the following columns: 
                electron_number     electron_energy     electron_occupation
        """
        import re 
        result = []
        p = re.compile("(\-?\d+\.?\d*)\s+(\-?\d+\.?\d*)\s+(\-?\d+\.?\d*)")
        stringLines = string.split("\n")
        for line in stringLines:
            match = p.findall(line)
            if match:
                if len(match)==1:
                   # print line
                    niveau = match[0]
                    result.append({"number": niveau[0], "energy":niveau[1], "occupation":niveau[2]})
                    #print niveaus
                else: 
                    break
        return result
    def getConfiguration(self):
        return self._parseFile()
    def showASCII(self):
        if self.spin:
            if self.spinOccupation:
                nelectrons = min(len(self.spinOccupation["1"]), len(self.spinOccupation["2"]))
                for i in range(nelectrons-1,-1,-1):
                    niveau1 = self.spinOccupation["1"][i]
                    niveau2 = self.spinOccupation["2"][i]
                    if niveau1["number"]==niveau2["number"]==str(i):
                        occupation1 = abs(float(niveau1["occupation"]))
                        occupation2 = abs(float(niveau2["occupation"]))
                        occupiedSymbol=""
                        if occupation1 or occupation2: 
                            occupiedSymbol="+"
                        print("%s.\t[%.1f][%.1f]  (%s) \t %s"%(i, occupation1, occupation2, niveau1["energy"], occupiedSymbol ))

            else:
                self.vprint("To show ASCII representation you first have to generate read the electron configuration", True)
    def showHTML(self):
        pass
