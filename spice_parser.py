class Component:
    def __init__(self, spl:list):
        self.parts = spl
        self.name = spl[0]
        if(self.name[0] == 'V'):
            self.wires = spl[1:3]
            self.Vdef = spl[3:]
        elif(self.name[0] == 'R'):
            self.wires = spl[1:3]
            self.Rdef = spl[3:]
        elif(self.name[0] == 'C'):
            self.wires = spl[1:3]
            self.Cdef = spl[3:]
        elif(self.name[0] == 'M'):
            self.wires = spl[1:5]
            self.Mdef = spl[5:]
        elif(self.name[0] == 'X'):
            self.wires = spl[1:-1]
            self.Xdef = spl[-1:]
        else:
            raise ValueError('Invalid Component')


# Rtest = "Rs_M4 Vss Vss_par_M4 0.1"
# Ctest = "Cds_M3 Y_par_M3 Vss_par_M3 1e-15"
# Mtest = "M3 Y_par_M3 A_par_M3 Vss_par_M3 Vss_par_M3 cmosn L=1u W=10u"
# Xtest = "X1 D E S NAND"

class Tok:
    def __init__(self, spl:list[str]):
        self.parts: list[str] = spl
    def asComp(self):
        try:
            return Component(self.parts)
        except ValueError as e:
            return None
    def __str__(self):
        return " ".join(self.parts)
TokList = list[Tok]
CompList = list[Component]
PortList = list[str]
class SubCkt:
    def __init__(self, name:str, ports:PortList):
        self.name = name
        self.ports = ports
        self.body: CompList = []
class Circuit:
    def __init__(self):
        self.title = ""
        self.globals:list[str] = []
        self.models:list[list[str]] = []
        self.body:TokList = []
        self.subckts: list[SubCkt] = []

def tok_get_name(tok: Tok):
    pass

def readSpiceNetlist(file_path) -> TokList:
    res = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("*"): continue
            spl = line.split()
            if spl[0] == '.include':
                for subins in readSpiceNetlist(spl[1]): # naive preproc
                    res.append(subins)
            else:
                res.append(Tok(spl))
    return res

def toCircuit(toklist: TokList):
    res = Circuit()
    curSubCkt = None
    for tok in toklist:
        parts = tok.parts
        if parts[0].upper() == '.TITLE':
            res.title = parts[1]
        elif parts[0].upper() == '.GLOBAL':
            res.globals = parts[1:]
        elif parts[0].upper() == '.MODEL':
            res.models.append(parts[1:])
        elif parts[0].upper() == '.SUBCKT':
            curSubCkt = SubCkt(parts[1], parts[2:])
        elif parts[0].upper() == '.ENDS':
            if(curSubCkt):
                res.subckts.append(curSubCkt)
            curSubCkt = None
        # elif parts[0].upper() == '.TRAN':
        #     pass
        # elif parts[0].upper() == '.CONTROL':
        #     pass
        # elif parts[0].upper() == '.ENDC':
        #     pass


    return res

def toSpiceNetlist(toklist: TokList):
    return '\n'.join([str(tok) for tok in toklist])

toklist = readSpiceNetlist('./counter_tb_spice.cir')
circ = toCircuit(toklist)
netlist = toSpiceNetlist(toklist)
print(netlist)
