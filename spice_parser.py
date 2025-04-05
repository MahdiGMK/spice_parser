from ast import Compare


class Component:
    def __init__(self, spl:list):
        self.name = spl[0]
        if(self.name[0] == 'V'):
            self.wires = spl[1:3]
            self.Mdef = spl[3:]
        elif(self.name[0] == 'R'):
            self.wires = spl[1:3]
            self.Mdef = spl[3:]
        elif(self.name[0] == 'C'):
            self.wires = spl[1:3]
            self.Mdef = spl[3:]
        elif(self.name[0] == 'M'):
            self.wires = spl[1:5]
            self.Mdef = spl[5:]
        elif(self.name[0] == 'X'):
            self.wires = spl[1:-1]
            self.Mdef = spl[-1:]
        else:
            raise ValueError('Invalid Component')
    def __str__(self) -> str:
        return f'{self.name} {' '.join(self.wires)} {' '.join(self.Mdef)}'


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
    def __str__(self) -> str:
        return f'''
.SUBCKT {self.name} {' '.join(self.ports)}
{'\n'.join([str(comp) for comp in self.body])}
.ENDS '''
class Circuit:
    def __init__(self):
        self.title = ""
        self.globals:list[str] = []
        self.models:list[list[str]] = []
        self.body:TokList = []
        self.subckts: list[SubCkt] = []
    def __str__(self) -> str:
        return (f'''
.TITLE {self.title}
.GLOBAL {' '.join(self.globals)}
{'\n'.join([f'.MODEL {' '.join(m)}' for m in self.models])}
{'\n'.join([str(subckt) for subckt in self.subckts])}
{'\n'.join([str(tok) for tok in self.body])} ''')

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
                import os
                incpath = os.path.dirname(file_path)+'/'+spl[1]
                for subins in readSpiceNetlist(incpath): # naive preproc
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
            if curSubCkt:
                res.subckts.append(curSubCkt)
            curSubCkt = None
        elif curSubCkt:
            comp = tok.asComp()
            if comp:
                curSubCkt.body.append(comp)
            else:
                raise ValueError("Invalid Component inside SubCkt")
        else:
            res.body.append(tok)
    return res

def addParasiticResistance(subckt: SubCkt, res = 0.1):
    allwires = []
    new_comp = []
    for comp in subckt.body:
        before_res = comp.wires
        after_res = []
        for w in before_res:
            res_name = f'R_gen_{comp.name}__{len(after_res)}'
            new_comp.append(Component([res_name , res_name , w , str(res)]))
            after_res.append(res_name)
        comp.wires = after_res
    for comp in new_comp:
        subckt.body.append(comp)

def addParasiticCapacitance(subckt: SubCkt, cap = '0.1p'):
    allwires = []
    for comp in subckt.body:
        for w in comp.wires:
            allwires.append(w)
    for x in set(allwires):
        subckt.body.append(Component([f'C_gen_{x}' , '0' , x , str(cap)]))

toklist = readSpiceNetlist('../counter_tb_spice.cir')
circ = toCircuit(toklist)
for subckt in circ.subckts:
    addParasiticResistance(subckt)
    addParasiticCapacitance(subckt)
print(circ)
