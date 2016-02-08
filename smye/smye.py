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
    def getLastOccuppiedStates(self, spin):
        """
        Returns a dict
            {"valence":occupancy, "conduction":last}
        with the valence state and the conduction (first unoccupied state) state
        """
        self.vprint("Getting extremal states ...")
        last = None
        configuration = self.spinOccupation[spin]
        for index, occupancy in enumerate(configuration[1:]):
            if float(occupancy["occupation"]) <.5:
                self.vprint("Found extremal states:")
                self.vprint("\tValence state: %s"%last)
                self.vprint("\tConduction state: %s"%occupancy)
                return {"valence":last, "conduction":occupancy, "index": index}
            last = occupancy
    def getNthExcitedState(self, n, spin):
        if self.spin:
            if not spin in ["1","2"]:
                print("Spin must be either 1 or 2")
                sys.exit(1)
            self.vprint("Getting %sth excited state for spin %s"%(n,spin))
            lastIndex = self.getLastOccuppiedStates(spin)["index"]
            newIndex = lastIndex - n
            self.vprint("Got it with index %s"%newIndex)
            return self.spinOccupation[spin][newIndex]
    def getNthExcitedEnergy(self, n, spin):
        state = self.getNthExcitedState(n,spin)
        self.vprint("Getting energy for electrinic state %s"%state)
        print(state["energy"])
    def getBandGap(self):
        if self.spin:
            self.vprint("Getting band gap for the case of two spins...");
            configuration     = self.spinOccupation;
            valence_states    = []
            conduction_states = []
            for spin in configuration:
                self.vprint("Getting bandgap information for spin %s"%spin)
                states             = self.getLastOccuppiedStates(spin)
                valence_states    += [ states["valence"] ]
                conduction_states += [ states["conduction"] ]
            if float( valence_states[0]["energy"] ) > float( valence_states[1]["energy"] ):
                valence = valence_states[0]
            else:
                valence = valence_states[1]
            if float( conduction_states[0]["energy"] ) < float( conduction_states[1]["energy"] ):
                conduction = conduction_states[0]
            else:
                conduction = conduction_states[1]
            general_bandgap = float(conduction["energy"]) - float(valence["energy"])
            print("VB %s"%valence["energy"])
            print("LB %s"%conduction["energy"])
            print("BG %s"%(general_bandgap))
            return (general_bandgap)
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
