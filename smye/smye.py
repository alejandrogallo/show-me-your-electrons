import os, sys

VERBOSE=False

class Diagram(object):

    """
    This class represents a parsed diagram, the methods of this class are used
    to extract information of the electronic configuration stored in the class.

    It needs to be given upon initializazion a file to read the electronic
    structure from. At the moment it assumes that the format of the file is in
    the OUTCAR form of the VASP program.
    """

    def __init__(self, filePath, verbose=VERBOSE, spin=True):
        self.filePath       = filePath
        self.verbose        = verbose
        self.spin           = spin
        self._configuration = None

    def vprint(self, something, err=False):
        if self.verbose:
            if not err :
                print("Diagram:: %s"%something)
            else:
                raise Exception("Diagram::ERROR:: %s"%something)

    def _parseFile(self):
        """
        This function parses the electronic configuration of the filePath
        """
        try:
            self.vprint("Trying to open file %s"%self.filePath)
            fd = open(self.filePath,"r")
        except IOError, e:
            self.vprint("File %s could not be opened"%self.filePath, True)
            raise IOError(e)
        else:
            self.vprint("Reading file")
            fileBuffer = fd.read()
            self.vprint("WARNING: ONLY WORKS FOR ONE K-POINT")
            if self.spin:
                return self._parseWithSpin(fileBuffer)
            else:
                return self._parseWithoutSpin(fileBuffer)

    def _parseWithoutSpin(self, fileBuffer):
        """
        It does what it says

        :fileBuffer: TODO
        :returns: TODO

        """
        occupation = [];
        self.vprint("Parsing electronic configuration without spin");
        identificationString="  band No.  band energies     occupation ";
        downSeparator="-------";
        occupationBuffer = fileBuffer.split(identificationString);
        if len(occupationBuffer)==1:
            self.vprint("There is no '%s' part in file %s, I AM NOT ABLE TO FIND ELECTRONIC INFORMATION"%(identificationString, self.filePath), True)
            sys.exit(-1)
        else:
            lastOccupationBuffer        = occupationBuffer[-1]
            lastOccupationBufferCleaned = lastOccupationBuffer.split(downSeparator)
            if len(lastOccupationBufferCleaned)==1:
                self.vprint("There was a problem parsing the information ", True)
            else:
                occupation=self._parseElectronicConfiguration(lastOccupationBufferCleaned[0])
        # self.vprint("Occupation parsed is : %s"%occupation)
        return occupation

    def _parseWithSpin(self, fileBuffer):
        spinOccupation = {"1":[], "2":[]}
        separator      = {"1":"spin component 2", "2":"-----"}
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
                lastSpinBuffer        = spinBuffer[-1]
                lastSpinBufferCleaned = lastSpinBuffer.split(separator[spin])
                if len(lastSpinBufferCleaned)==1:
                    self.vprint("There was a problem parsing the information for spin %s"%(spin), True)
                else:
                    spinOccupation[spin]=self._parseElectronicConfiguration(lastSpinBufferCleaned[0])
                    #print spinOccupation[spin]
        return spinOccupation

    def _parseElectronicConfiguration(self, string):

        """
        This function parses the electronic configuration from a string
        (fileBuffer) The format of the string should be a table with the
        following columns:

         | electron_number | electron_energy | electron_occupation |

        """

        import re
        result      = []
        p           = re.compile("(\-?\d+\.?\d*)\s+(\-?\d+\.?\d*)\s+(\-?\d+\.?\d*)")
        stringLines = string.split("\n")
        for line in stringLines:
            match = p.findall(line)
            if match:
                if len(match) == 1:
                    niveau = match[0]
                    result.append({"number": niveau[0], "energy":niveau[1], "occupation":niveau[2]})
                else:
                    break
        return result


    def getConfigurationWith(self, spin=-1, occupied=True):
        occupied_states = []
        if self.spin:
            if not spin in ["1","2"]:
                print("Spin must be either 1 or 2")
                sys.exit(1)
            configuration = self.getConfiguration()[spin]
        else:
            configuration = self.getConfiguration()
        for state in configuration:
            if occupied:
                if float(state["occupation"]):
                    occupied_states.append(state)
            else:
                if not float(state["occupation"]):
                    occupied_states.append(state)
        return occupied_states

    def getUnoccupiedStates(self, spin=-1):
        """TODO: Docstring for getOccupiedStates.

        :spin: TODO
        :returns: TODO

        """
        return self.getConfigurationWith(spin, occupied=False)

    def getOccupiedStates(self, spin=-1):
        """TODO: Docstring for getOccupiedStates.

        :spin: TODO
        :returns: TODO

        """
        return self.getConfigurationWith(spin, occupied=True)

    def getNthLeastEnergeticStateWith(self, n, spin=-1, occupied=True):
        """
        Get the nth least energetic state of occupied or unoccupied states
            e.g.: 1 = least energetic usw..
        We make n loops finding the most energetic occupied states and taking
        them out of the list
        """
        states = self.getConfigurationWith(spin, occupied)
        popIndex = -1
        bottle = None
        for i in range(n):
            bottle = states[-1]
            for j, state in enumerate(states):
                if self._geq(bottle, state):
                    self.vprint(bottle)
                    bottle=state
                    popIndex=j
            # erase maximum from the list
            states.pop(popIndex)
        return bottle

    def getNthMostEnergeticStateWith(self, n, spin=-1, occupied=True):
        """
        Get the nth most energetic state of occupied or unoccupied states
            e.g.: 1 = most energetic usw..
        We make n loops finding the most energetic occupied states and taking
        them out of the list
        """
        states = self.getConfigurationWith(spin, occupied)
        popIndex = -1
        bottle = None
        for i in range(n):
            bottle = states[-1]
            for j, state in enumerate(states):
                if self._geq(state, bottle):
                    self.vprint(bottle)
                    bottle=state
                    popIndex=j
            # erase maximum from the list
            states.pop(popIndex)
        return bottle

    def getNthExcitedState(self, n, spin=-1):
        """
        Get the nth most energetic state
            e.g.: 1 = most energetic usw..
        We make n loops finding the most energetic occupied states and taking
        them out of the list
        """
        return self.getNthMostEnergeticStateWith(n, spin, occupied=True)

    def _leq(self, state1, state2):
        """
        Compares the energy of two states
        """
        if float(state1["energy"])<=float(state2["energy"]):
            return True
        else:
            return False

    def _geq(self, state1, state2):
        """
        Compares the energy of two states
        """
        if float(state1["energy"])>=float(state2["energy"]):
            return True
        else:
            return False

    def getNLastMostEnergeticStatesWith(self, n, occupied=True):
        """
        *
        *
        *  +
           +

        *
        *
        """
        if self.spin:
            classified_states = []
            get = "both"
            j   = 1
            k   = 1
            # init = True
            for i in range(1,int(n)+1):
                if get == "1" or get == "both":
                    if get == "both":
                        self.vprint("init")
                        last         = self.getNthOrderedState(k, spin="2", occupied=occupied)
                        last["spin"] = "2";
                        spin_last    = "2"
                        k+=1;
                    new         = self.getNthOrderedState(j, spin="1", occupied=occupied)
                    new["spin"] = "1";
                    spin_new    = "1"
                    j+=1;
                else:
                    new         = self.getNthOrderedState(k, spin="2", occupied=occupied)
                    new["spin"] = "2";
                    spin_new    = "2"
                    k+=1;
                self.vprint("new %s"%new)
                self.vprint("last %s"%last)
                if self._geq(new, last):
                    classified_states.append(new)
                    get  = spin_new
                else:
                    self.vprint("change")
                    classified_states.append(last)
                    last      = new
                    get       = spin_last
                    spin_last = spin_new
            return classified_states
        else:
            classified_states = [];
            for i in range(1, int(n)+1):
                classified_states.append(self.getNthMostEnergeticStateWith(i,occupied=occupied))
            return classified_states

    def getNLastExcitedStates(self, n):
        return self.getNLastMostEnergeticStatesWith(n, occupied=True)

    def printNLastExcitedStates(self, n):
        states = self.getNLastExcitedStates(n)
        for state in states:
            print("%s %s"%(state["spin"], state["energy"]))

    def getAllLastNStates(self, down_offset, up_offset=0):
        if self.spin:
            last      = self.getNLastExcitedStates(1)[0]
            lastIndex = last["number"]
            # now get everything down_offset underneath
            result_states = []
            for i in range(0,down_offset+1):
                newIndex = int(lastIndex) - i
                for spin in ["1", "2"]:
                    newState          = self.getStateByBandNumber(spin, newIndex);
                    newState["spin" ] = spin
                    result_states.append(newState)
            for i in range(1,up_offset+1):
                newIndex = int(lastIndex) + i
                for spin in ["1", "2"]:
                    newState          = self.getStateByBandNumber(spin, newIndex);
                    newState["spin" ] = spin
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

    def getStateByBandNumber(self, spin, index):
        if self.spin:
            configuration = self.getConfiguration()[spin]
        else:
            configuration = self.getConfiguration()
        for state in configuration:
            if float(state["number"]) == float(index):
                return state
        return None

    def getLastOccuppiedStates(self, spin=-1):
        self.vprint("Getting last occupied state ...")
        return self.getNthExcitedState(1,spin)

    def getValenceStates(self, spin):
        """
        Returns a dict
            {"valence": valence_state, "conduction": conduction_state}
        with the valence state and the conduction (first unoccupied state)
        state
        """
        valence    = self.getLastOccuppiedStates( spin )
        lastIndex  = valence["number"]
        condIndex  = int(lastIndex)+1
        conduction = self.getStateByBandNumber(spin, condIndex)
        if conduction:
            return {"valence": valence, "conduction": conduction}
        else:
            raise Exception("Conduction state was not found!")
            return False

    def getBandGap(self):
        """
        Gets the bandgap out of the electronic configuration
        """
        if self.spin:
            self.vprint("Getting band gap for the case of two spins...");
            # configuration     = self.getConfiguration();
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
            print("HOMO %s"%(valence))
            print("LUMO %s"%(conduction))
            return (general_bandgap)
        else:
            self.vprint("Getting band gap for the case of no spin ...");
            configuration = self.getConfiguration();
            valence       = {"energy":0, "occupation": 0}
            conduction    = {"energy":10000000, "occupation": 1}
            for state in configuration:
                if float(state["occupation"]) > 0:
                    if self._geq(state, valence):
                        valence = state
                else:
                    if self._geq(conduction, state):
                        conduction = state
            general_bandgap = float(conduction["energy"]) - float(valence["energy"])
            print("VB %s"%valence["energy"])
            print("LB %s"%conduction["energy"])
            print("BG %s"%(general_bandgap))
            print("HOMO %s"%(valence))
            print("LUMO %s"%(conduction))
            return (general_bandgap)

    def getConfiguration(self):

        """
        General getter for the electronic occupation, if the occupation has not
        been parsed from the file, it parses it, else it just returns the
        previously parsed configuration
        """

        if not self._configuration:
            self._configuration = self._parseFile()
        return self._configuration

    def showASCII(self):
        """
        Produces a crude ASCII representation of the electronic occupation
        """
        if self.spin:
            nelectrons = min(len(self.getConfiguration()["1"]), len(self.getConfiguration()["2"]))
            for i in range(nelectrons-1,-1,-1):
                niveau1 = self.getConfiguration()["1"][i]
                niveau2 = self.getConfiguration()["2"][i]
                if niveau1["number"]==niveau2["number"]==str(i):
                    occupation1 = 0.5
                    occupation1 = abs(float(niveau1["occupation"]))
                    occupation2 = abs(float(niveau2["occupation"]))
                    occupiedSymbol=""
                    if occupation1 or occupation2:
                        occupiedSymbol="+"
                        draw = True
                    else:
                        draw = False
                    if not occupation1:
                        occupation1 = " "
                    if not occupation2:
                        occupation2 = " "
                    if draw:
                        print("%s.\t(%s) [%s][%s] (%s) %s"%(i, niveau2["energy"], occupation1, occupation2, niveau1["energy"], occupiedSymbol ))
        else:
            nelectrons = len(self.getConfiguration())
            for i in range(nelectrons-1,0,-1):
                niveau = self.getConfiguration()[i-1]
                # if niveau["number"]==niveau2["number"]==str(i):
                # occupation = 0.5
                occupation = abs(float(niveau["occupation"]))
                occupiedSymbol=""
                if occupation:
                    occupiedSymbol="+"
                    draw = True
                else:
                    draw = False
                if not occupation:
                    occupation = " "
                if draw:
                    print("%s.\t(%s) [%s] %s"%(i, niveau["energy"], occupation, occupiedSymbol ))
