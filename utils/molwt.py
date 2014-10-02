#Well, the syntax of a formula is recursively defined:  each chunk of the
#expression is either an element name, or is itself an expression enclosed in
#parentheses (that's the recursion <wink>), and in either case followed by an
#optional "repeat count".
#
#Parsing isn't easy, but can be learned.  I'm going to attach a complete
#solution to this one, allowing you to type e.g.
#
#D:\Python>python misc/molw.py
#? H2O
#input must have two fields
#? molw H2O
#molecular weight 18.0152
#? syms H2O
#H (Hydrogen): 2
#O (Oxygen): 1
#? molw NaCl
#molecular weight 58.44277
#? syms (H2O4)12
#H (Hydrogen): 24
#O (Oxygen): 48
#? PbUr
#input must have two fields
#? molw PbU
#molecular weight 445.229
#? syms PbU
#Pb (Lead): 1
#U (Uranium): 1
#? molw Mg(NO3)2
#molecular weight 148.3148
#? syms Mg(NO3)2
#Mg (Magnesium): 1
#N (Nitrogen): 2
#O (Oxygen): 6
#? molw ClAp
#'Ap' is not an element symbol:
#ClAp
#  ^
#
#?
#
#The parsing technique here is called "recursive descent with one token
#lookahead".  That may all sound like gibberish now, but once you understand
#the (simple) code, each word in that will be seen to have a definite
#meaning.  The structure of the parsing code matches the informal English
#recursive definition above very closely.  That's the great advantage of
#recursive descent:  it's inuitive.
#
#You'll find that it won't accept any illegal formulas, but that sometimes
#the error msgs it produces are odd.  This should give you a lot of sympathy
#for Guido's job <0.9 wink>.
#
#Apart from the parser, there's a Tokenizer class here that's a bit of
#overkill in this particular context.  The tokenizer simply looks at "the
#next" piece of the formula, and classifies the first chunk of it as to
#whether it looks like a parenthesis, element name, repeat count, or end of
#input.  The *kind* of token is stored in global ttype, and the *value* of
#the token is stored in global tvalue.  The parsing code makes its decisions
#based on ttype, and uses tvalue as needed to extract specific information.
#
#This is a classic structure for parsers, and works very well in practice --
#provided you get used to it first, and don't get too terribly ambitious.
#Before the advent of machine-generated table-driven parsers, entire
#compilers (e.g. Pascal's) were written "by hand" this way.  It's easy enough
#to pick up that everyone ought to learn how to do it -- which is why I'm
#posting the whole thing to the tutor list <wink>.
#
#The rest of it is simpler, and should remind you of the series/parallel
#circuit example Gordon posted to c.l.py a while back.  A formula is a
#sequence of elements and subformulas, and an ElementSequence class models
#that as a list (a list of what?  of Elements and other ElementSequences!
#again this matches the English description very closely).  It's trivial for
#an Element to report its own weight, and an ElementSequence just has to ask
#its contained guys for their weights and sum them up.
#
#recursion-is-your-friend-because-nature-is-recursive-ly y'rs  - tim
# symbol, name, atomic number, molecular weight
_data = r"""'Ac', 'Actinium', 89, 227
'Ag', 'Silver', 47, 107.868
'Al', 'Aluminum', 13, 26.98154
'Am', 'Americium', 95, 243
'Ar', 'Argon', 18, 39.948
'As', 'Arsenic', 33, 74.9216
'At', 'Astatine', 85, 210
'Au', 'Gold', 79, 196.9665
'B', 'Boron', 5, 10.81
'Ba', 'Barium', 56, 137.33
'Be', 'Beryllium', 4, 9.01218
'Bi', 'Bismuth', 83, 208.9804
'Bk', 'Berkelium', 97, 247
'Br', 'Bromine', 35, 79.904
'C', 'Carbon', 6, 12.011
'Ca', 'Calcium', 20, 40.08
'Cd', 'Cadmium', 48, 112.41
'Ce', 'Cerium', 58, 140.12
'Cf', 'Californium', 98, 251
'Cl', 'Chlorine', 17, 35.453
'Cm', 'Curium', 96, 247
'Co', 'Cobalt', 27, 58.9332
'Cr', 'Chromium', 24, 51.996
'Cs', 'Cesium', 55, 132.9054
'Cu', 'Copper', 29, 63.546
'Dy', 'Dysprosium', 66, 162.50
'Er', 'Erbium', 68, 167.26
'Es', 'Einsteinium', 99, 254
'Eu', 'Europium', 63, 151.96
'F', 'Fluorine', 9, 18.998403
'Fe', 'Iron', 26, 55.847
'Fm', 'Fermium', 100, 257
'Fr', 'Francium', 87, 223
'Ga', 'Gallium', 31, 69.735
'Gd', 'Gadolinium', 64, 157.25
'Ge', 'Germanium', 32, 72.59
'H', 'Hydrogen', 1, 1.0079
'He', 'Helium', 2, 4.0026
'Hf', 'Hafnium', 72, 178.49
'Hg', 'Mercury', 80, 200.59
'Ho', 'Holmium', 67, 164.9304
'I', 'Iodine', 53, 126.9045
'In', 'Indium', 49, 114.82
'Ir', 'Iridium', 77, 192.22
'K', 'Potassium', 19, 39.0983
'Kr', 'Krypton', 36, 83.80
'La', 'Lanthanum', 57, 138.9055
'Li', 'Lithium', 3, 6.94
'Lr', 'Lawrencium', 103, 260
'Lu', 'Lutetium', 71, 174.96
'Md', 'Mendelevium', 101, 258
'Mg', 'Magnesium', 12, 24.305
'Mn', 'Manganese', 25, 54.9380
'Mo', 'Molybdenum', 42, 95.94
'N', 'Nitrogen', 7, 14.0067
'Na', 'Sodium', 11, 22.98977
'Nb', 'Niobium', 41, 92.9064
'Nd', 'Neodymium', 60, 144.24
'Ne', 'Neon', 10, 20.17
'Ni', 'Nickel', 28, 58.71
'No', 'Nobelium', 102, 259
'Np', 'Neptunium', 93, 237.0482
'O', 'Oxygen', 8, 15.9994
'Os', 'Osmium', 76, 190.2
'P', 'Phosphorous', 15, 30.97376
'Pa', 'Proactinium', 91, 231.0359
'Pb', 'Lead', 82, 207.2
'Pd', 'Palladium', 46, 106.4
'Pm', 'Promethium', 61, 145
'Po', 'Polonium', 84, 209
'Pr', 'Praseodymium', 59, 140.9077
'Pt', 'Platinum', 78, 195.09
'Pu', 'Plutonium', 94, 244
'Ra', 'Radium', 88, 226.0254
'Rb', 'Rubidium', 37, 85.467
'Re', 'Rhenium', 75, 186.207
'Rh', 'Rhodium', 45, 102.9055
'Rn', 'Radon', 86, 222
'Ru', 'Ruthenium', 44, 101.07
'S', 'Sulfur', 16, 32.06
'Sb', 'Antimony', 51, 121.75
'Sc', 'Scandium', 21, 44.9559
'Se', 'Selenium', 34, 78.96
'Si', 'Silicon', 14, 28.0855
'Sm', 'Samarium', 62, 150.4
'Sn', 'Tin', 50, 118.69
'Sr', 'Strontium', 38, 87.62
'Ta', 'Tantalum', 73, 180.947
'Tb', 'Terbium', 65, 158.9254
'Tc', 'Technetium', 43, 98.9062
'Te', 'Tellurium', 52, 127.60
'Th', 'Thorium', 90, 232.0381
'Ti', 'Titanium', 22, 47.90
'Tl', 'Thallium', 81, 204.37
'Tm', 'Thulium', 69, 168.9342
'U', 'Uranium', 92, 238.029
'Unh', 'Unnilhexium', 106, 263
'Unp', 'Unnilpentium', 105, 260
'Unq', 'Unnilquadium', 104, 260
'Uns', 'Unnilseptium', 107, 262
'V', 'Vanadium', 23, 50.9415
'W', 'Tungsten', 74, 183.85
'Xe', 'Xenon', 54, 131.30
'Y', 'Yttrium', 39, 88.9059
'Yb', 'Ytterbium', 70, 173.04
'Zn', 'Zinc', 30, 65.38
'Zr', 'Zirconium', 40, 91.22"""

class Element:
    def __init__(self, symbol, name, atomicnumber, molweight):
        self.sym = symbol
        self.name = name
        self.ano = atomicnumber
        self.mw = molweight

    def getweight(self):
        return self.mw

    def addsyms(self, weight, result):
        result[self.sym] = result.get(self.sym, 0) + weight

def build_dict(s):
    import string
    answer = {}
    for line in string.split(s, "\n"):
        symbol, name, num, weight = eval(line)
        answer[symbol] = Element(symbol, name, num, weight)
    return answer

sym2elt = build_dict(_data)
del _data

class ElementSequence:
    def __init__(self, *seq):
        self.seq = list(seq)
        self.count = 1

    def append(self, thing):
        self.seq.append(thing)

    def getweight(self):
        sum = 0.0
        for thing in self.seq:
            sum = sum + thing.getweight()
        return sum * self.count

    def set_count(self, n):
        self.count = n

    def __len__(self):
        return len(self.seq)

    def addsyms(self, weight, result):
        totalweight = weight * self.count
        for thing in self.seq:
            thing.addsyms(totalweight, result)

    def displaysyms(self):
        result = {}
        self.addsyms(1, result)
        items = result.items()
        items.sort()
        for sym, count in items:
            print sym, "(" + sym2elt[sym].name + "):", count

NAME, NUM, LPAREN, RPAREN, EOS = range(5)
import re
_lexer = re.compile(r"[A-Z][a-z]*|\d+|[()]|<EOS>").match
del re

class Tokenizer:
    def __init__(self, input):
        self.input = input + "<EOS>"
        self.i = 0

    def gettoken(self):
        global ttype, tvalue
        self.lasti = self.i
        m = _lexer(self.input, self.i)
        if m is None:
            self.error("unexpected character")
        self.i = m.end()
        tvalue = m.group()
        if tvalue == "(":
            ttype = LPAREN
        elif tvalue == ")":
            ttype = RPAREN
        elif tvalue == "<EOS>":
            ttype = EOS
        elif "0" <= tvalue[0] <= "9":
            ttype = NUM
            tvalue = int(tvalue)
        else:
            ttype = NAME

    def error(self, msg):
        emsg = msg + ":\n"
        emsg = emsg + self.input[:-5] + "\n"  # strip <EOS>
        emsg = emsg + " " * self.lasti + "^\n"
        raise ValueError(emsg)

def parse(s):
    global t, ttype, tvalue
    t = Tokenizer(s)
    t.gettoken()
    seq = parse_sequence()
    if ttype != EOS:
        t.error("expected end of input")
    return seq

def parse_sequence():
    global t, ttype, tvalue
    seq = ElementSequence()
    while ttype in (LPAREN, NAME):
        # parenthesized expression or straight name
        if ttype == LPAREN:
            t.gettoken()
            thisguy = parse_sequence()
            if ttype != RPAREN:
                t.error("expected right paren")
            t.gettoken()
        else:
            assert ttype == NAME
            if sym2elt.has_key(tvalue):
                thisguy = ElementSequence(sym2elt[tvalue])
            else:
                t.error("'" + tvalue + "' is not an element symbol")
            t.gettoken()
        # followed by optional count
        if ttype == NUM:
            thisguy.set_count(tvalue)
            t.gettoken()
        seq.append(thisguy)
    if len(seq) == 0:
        t.error("empty sequence")
    return seq

import string
while 1:
    x = raw_input("? ")
    #fields = string.split(x)
    #if len(fields) != 2:
    #    print "input must have two fields"
    #    continue
    #action, formula = fields
    #ok = 0
    try:
        #seq = parse(formula)
        seq = parse(x)
        ok = 1
    except ValueError, detail:
        print str(detail)
    print "molecular weight", seq.getweight()
    #if not ok:
    #    continue
    #if action == "molw":
    #    print "molecular weight", seq.getweight()
    #elif action == "syms":
    #    seq.displaysyms()
    #else:
    #    print "unknown action:", action
