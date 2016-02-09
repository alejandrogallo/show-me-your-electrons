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
        self.vprint("Getting last occupied state ...")
        return self.getNthExcitedState(1,spin)
    def getNthExcitedState(self, n, spin):
        if self.spin:
            if not spin in ["1","2"]:
                print("Spin must be either 1 or 2")
                sys.exit(1)
            spin_configuration = self.spinOccupation[spin]
            occupied_states = []
            for state in spin_configuration:
                if float(state["occupation"]):
                    occupied_states.append(state)
            return occupied_states[-n]
    def _geq(self, state1, state2):
        """
        Compares the energy of two states
        """
        if float(state1["energy"])>=float(state2["energy"]):
            return True
        else:
            return False
    def getNLastExcitedStates(self, n):
        """
        *        
        *        
        *  +     
           +     
                 
        *        
        *        
        """
        classified_states = []
        get = "both"
        j = 1
        k = 1
        # init = True
        for i in range(1,int(n)+1):
            if get == "1" or get == "both":
                if get == "both":
                    self.vprint("init")
                    last = self.getNthExcitedState(k, "2")
                    last["spin"] = "2";
                    spin_last = "2"
                    k+=1;
                new = self.getNthExcitedState(j, "1")
                new["spin"] = "1";
                spin_new = "1"
                j+=1;
            else:
                new = self.getNthExcitedState(k, "2")
                new["spin"] = "2";
                spin_new = "2"
                k+=1;
            self.vprint("new %s"%new)
            self.vprint("last %s"%last)
            if self._geq(new, last):
                classified_states.append(new)
                get  = spin_new
            else:
                self.vprint("change")
                classified_states.append(last)
                last = new
                get  = spin_last
                spin_last = spin_new
        return classified_states
    def printNLastExcitedStates(self, n):
        states = self.getNLastExcitedStates(n)
        for state in states:
            print("%s %s"%(state["spin"], state["energy"]))
    def getAllLastNStates(self, down_offset, up_offset=0):
        last = self.getNLastExcitedStates(1)[0]
        print last
        lastIndex = last["number"]
        # now get everything down_offset underneath
        result_states = []
        for i in range(0,down_offset+1):
            newIndex = int(lastIndex) - i
            for spin in ["1", "2"]:
                newState = self.getStateByIndex(spin, newIndex);
                newState["spin" ]=spin
                result_states.append(newState)
        for i in range(1,up_offset+1):
            newIndex = int(lastIndex) + i
            for spin in ["1", "2"]:
                newState = self.getStateByIndex(spin, newIndex);
                newState["spin" ]=spin
                result_states.append(newState)
        return result_states
    def printAllLastNStates(self, down_offset, up_offset=0):
        states = self.getAllLastNStates(down_offset, up_offset)
        for state in states:
            print("%s %s %s %s"%(state["spin"], state["energy"], state["occupation"], state["number"]))

    def getNthExcitedEnergy(self, n, spin):
        state = self.getNthExcitedState(n,spin)
        self.vprint("Getting energy for electrinic state %s"%state)
        print(state["energy"])
    def getStateByIndex(self, spin, index):
        for state in self.spinOccupation[spin]:
            if float(state["number"]) == float(index):
                return state
        return None
    def getValenceStates(self, spin):
        valence = self.getLastOccuppiedStates( spin )
        # print("VALENCE")
        # print(valence)
        lastIndex = valence["number"]
        condIndex = int(lastIndex)+1
        conduction = self.getStateByIndex(spin, condIndex)
        if conduction:
            return {"valence": valence, "conduction": conduction}
        else:
            raise Exception("Conduction state was not found!")
            return False
    def getBandGap(self):
        if self.spin:
            self.vprint("Getting band gap for the case of two spins...");
            # configuration     = self.spinOccupation;
            valence_states    = []
            conduction_states = []
            for spin in ["1", "2"]:
                self.vprint("Getting bandgap information for spin %s"%spin)
                states             = self.getValenceStates(spin)
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
