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

    def vprint(self, something, err=False, title="Diagram"):
        if self.verbose:
            if not err :
                print("%s:: %s"%(title, something))
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
            self.vprint("\033[0;31mWARNING:\033[0m ONLY WORKS FOR ONE K-POINT")
            if self.spin:
                return self._parseWithSpin(fileBuffer)
            else:
                return self._parseWithoutSpin(fileBuffer)

    def _addKeyToStates(self, states, key, value):
        for state in states:
            state[key]=value
        return states

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
            sys.exit(1)
        else:
            lastOccupationBuffer        = occupationBuffer[-1]
            lastOccupationBufferCleaned = lastOccupationBuffer.split(downSeparator)
            if len(lastOccupationBufferCleaned)==1:
                self.vprint("There was a problem parsing the information ", True)
            else:
                occupation=self._parseElectronicConfiguration(lastOccupationBufferCleaned[0])
        # we add a key to all states for completeness for the case with spin polarisation
        return self._addKeyToStates(occupation, "spin", 0)

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
                    preOccupation = self._parseElectronicConfiguration(lastSpinBufferCleaned[0])
                    # we add a key to all states to be able to differentiate between spins
                    spinOccupation[spin]=self._addKeyToStates(preOccupation, "spin", spin)
                    self.vprint("[   \033[0;31mOK\033[0m   ] Information for spin %s parsed"%spin)
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
                if "k-point" in line:
                    # fix for k-point appearing in OUTCAR
                    self.vprint("\tignoring line with k-point")
                    continue
                if len(match) == 1:
                    niveau = match[0]
                    result.append({"number": niveau[0], "energy":niveau[1], "occupation":niveau[2]})
                else:
                    break
        return result

    def _findTheNthExtremalEnergeticState(self, n, states, extreme):
        self.vprint("Finding the (%s)th extreme (%s)"%(n, extreme))
        popIndex = -1
        bottle = None
        for i in range(n):
            bottle = states[-1]
            for j, state in enumerate(states):
                if extreme == "least":
                    if self._geq(bottle, state):
                        # self.vprint(bottle)
                        bottle=state
                        popIndex=j
                else:
                    if self._geq(state, bottle):
                        # self.vprint(bottle)
                        bottle=state
                        popIndex=j
            # erase maximum from the list
            states.pop(popIndex)
        return bottle

    def getConfigurationWith(self, spin=-1, occupied=True):
        """
        Get configuration of occupied or unoccupied states
        also according to spin.

            Spin must be 1 or 2 if being calculating with
            spin polarisation

        Returns a list of states
        """
        states = []
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
                    states.append(state)
            else:
                if not float(state["occupation"]):
                    states.append(state)
        return states

    def getUnoccupiedStates(self, spin=-1):
        self.vprint("Getting \033[0;36munoccupied\033[0m states")
        return self.getConfigurationWith(spin, occupied=False)

    def getOccupiedStates(self, spin=-1):
        self.vprint("Getting \033[0;36moccupied\033[0m states")
        return self.getConfigurationWith(spin, occupied=True)

    def getStatesAboutFermiLevel(self, down_offset, up_offset):
        states = []
        # unoccupied states
        for i in range(up_offset, 0, -1):
            state = self.getNthLeastEnergeticState(i, occupied=False)
            states.append(state)
        # occupied states
        for i in range(1,down_offset+1):
            state = self.getNthMostEnergeticState(i, occupied=True)
            states.append(state)
        return states


    def getNthLeastEnergeticStateWith(self, n, spin=-1, occupied=True):
        """
        This is together with getNthMostEnergeticStateWith one of the main
        functions of the package.

        Get the nth least energetic state of occupied or unoccupied states
            e.g.: 1 = least energetic usw..
        We make n loops finding the most energetic occupied states and taking
        them out of the list
        """
        self.vprint("Getting the %sth least energetic state with spin=%s"%(n, spin))
        states = self.getConfigurationWith(spin, occupied)
        return self._findTheNthExtremalEnergeticState(n, states, "least")

    def getNthMostEnergeticStateWith(self, n, spin=-1, occupied=True):
        """
        Get the nth most energetic state of occupied or unoccupied states
            e.g.: 1 = most energetic usw..
        We make n loops finding the most energetic occupied states and taking
        them out of the list
        """
        self.vprint("Getting the %sth least energetic state with spin=%s"%(n, spin))
        states = self.getConfigurationWith(spin, occupied)
        return self._findTheNthExtremalEnergeticState(n, states, "most")

    def getNthExtremalEnergeticState(self, n, extreme, occupied=True):
        self.vprint("Getting the %sth %s energetic state with regardless of spin for occupied = %s"%(n, extreme, occupied))
        if self.spin:
            spin1_states = self.getConfigurationWith(spin="1", occupied=occupied)
            spin2_states = self.getConfigurationWith(spin="2", occupied=occupied)
            all_states = spin1_states + spin2_states
            return self._findTheNthExtremalEnergeticState(n, all_states, extreme)
        else:
            if extreme=="least":
                return self.getNthLeastEnergeticStateWith(n, spin=-1, occupied=occupied)
            else:
                return self.getNthMostEnergeticStateWith(n, spin=-1, occupied=occupied)

    def getNthMostEnergeticState(self, n, occupied):
        return self.getNthExtremalEnergeticState(n, "most", occupied=occupied)

    def getNthLeastEnergeticState(self, n, occupied):
        return self.getNthExtremalEnergeticState(n, "least", occupied=occupied)

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


    def printNthExcitedState(self, nArray):
        for n in nArray:
            if n < 0:
                state = self.getNthLeastEnergeticState(abs(n), occupied=False)
            else:
                state = self.getNthMostEnergeticState(n,occupied=True)
            print(state)

    def printStatesAboutFermiLevel(self, down_offset, up_offset=0):
        states = self.getStatesAboutFermiLevel(down_offset, up_offset)
        print("%s %s %s %s"%("spin", "energy", "occupation", "number"))
        for state in states:
            # print state
            print("%s %s %s %s"%(state["spin"], state["energy"], state["occupation"], state["number"]))

    def getHomo(self):
        self.vprint("Getting \033[0;36mHOMO\033[0m")
        return self.getNthMostEnergeticState(1, occupied=True)

    def getNettoSpin(self):
        """
        This sums the spin numbers of the array states
        and gives the netto spin of the system.

        :states: Array of states
        :returns: Spin

        """
        SPIN_1=0
        SPIN_2=0
        if not self.spin:
            raise Exception("To get the spin a polarised calcultion must be performed")
        self.vprint("Calculating netto spin")
        spin1=self.getOccupiedStates(spin="1")
        spin2=self.getOccupiedStates(spin="2")
        for state in spin1:
            SPIN_1+=float(state["occupation"])
        for state in spin2:
            SPIN_2+=float(state["occupation"])
        return abs(SPIN_1-SPIN_2)
    def getLumo(self):
        self.vprint("Getting \033[0;36mLUMO\033[0m")
        return self.getNthLeastEnergeticState(1, occupied=False)

    def getBandGap(self):
        """
        Gets the bandgap out of the electronic configuration
        """
        self.vprint("Getting bandgap information");
        valence = self.getHomo()
        conduction = self.getLumo()

        bandgap = float(conduction["energy"]) - float(valence["energy"])
        print("VB %s"%valence["energy"])
        print("LB %s"%conduction["energy"])
        print("BG %s"%(bandgap))
        print("HOMO %s"%(valence))
        print("LUMO %s"%(conduction))
        return bandgap

    def getConfiguration(self):

        """
        General getter for the electronic occupation, if the occupation has not
        been parsed from the file, it parses it, else it just returns the
        previously parsed configuration
        """

        if not self._configuration:
            self.vprint("Going to get configuration from file")
            self._configuration = self._parseFile()
        return self._configuration

    def mosAsymptote(self, states, *args, **kwargs):
        import mos
        print(mos.MOS_ASYMPTOTE(states, *args, **kwargs))


    def showASCII(self):
        """
        Produces a crude ASCII representation of the electronic occupation
        """
        if self.spin:
            states_spin1 = self.getConfiguration()["1"]
            states_spin2 = self.getConfiguration()["2"]
            nelectrons = min(len(states_spin1), len(states_spin2))
            for i in range(nelectrons-1,-1,-1):
                niveau1 = states_spin1[i]
                niveau2 = states_spin2[i]
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

