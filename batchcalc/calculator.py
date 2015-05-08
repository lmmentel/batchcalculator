# -*- coding: utf-8 -*-
#
#    Zeolite Batch Calculator
#
# A program for calculating the correct amount of reagents (batch) for a
# particular zeolite composition given by the molar ratio of its components.
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Lukasz Mentel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__version__ = "0.2.1"

import operator
import re

from numpy.linalg import solve, lstsq
import numpy as np

from batchcalc import controller as ctrl
from batchcalc.model import Chemical, Component, Batch

_MINWIDTH = 15

class BatchCalculator(object):

    def __init__(self, session):

        self.session = session

        self.lists = ["components", "chemicals"]

        # create lists for different categories of
        self.components = []
        self.chemicals = []

        self.calculated = False

        self.A = np.zeros(1)
        self.B = np.zeros(1)
        self.X = np.zeros(1)

        self.scale_all = 100.0
        self.sample_scale = 1.0
        self.sample_size = 5.0
        self.item_scale = 1.0
        self.selections = []

    def reset(self):
        '''
        Clear the state of the calculation by reseting all the list and
        variables.
        '''

        self.calculated = False

        self.components = []
        self.chemicals = []

        self.A = np.zeros(1)
        self.B = np.zeros(1)
        self.X = np.zeros(1)

        self.scale_all = 100.0
        self.sample_scale = 1.0
        self.sample_size = 5.0
        self.item_scale = 1.0
        self.selections = []

    # this can be probably removed since base chemical has is_undefined method
    @staticmethod
    def is_empty(item):
        if item is None or item in ["", "NULL", "None"]:
            return True
        else:
            return False

    def select_item(self, lst, attr, value):
        '''
        From a list of objects "lst" having a common attribute get the index of
        the object having the attribute "attr" set to "value".
        '''

        if lst not in self.lists:
            raise ValueError("wrong table in select_item")

        ag = operator.attrgetter(attr)
        for item in getattr(self, lst):
            if ag(item) == value:
                return item
        else:
            return None

    def calculate_masses(self):
        '''
        Solve the linear system of equations  B * X = C
        '''

        if len(self.components) == 0:
            raise ValueError("No Zeolite components selected")

        if len(self.chemicals) == 0:
            raise ValueError("No chemicals selected")

        for comp in self.components:
            temp = ctrl.get_chemicals(self.session, components=[comp])
            if len(set([t.id for t in temp]) & set([r.id for r in self.chemicals])) == 0:
                raise ValueError("some components need their sources: {0:s}".format(comp.name))

        self.A = self.get_A_matrix()
        self.B = self.get_B_matrix()

        try:
            if self.B.shape[0] == self.B.shape[1]:
                self.X = solve(np.transpose(self.B), self.A)
            else:
                self.X, resid, rank, s = lstsq(np.transpose(self.B), self.A)
            # assign calculated masses to the chemicals
            for chemical, x in zip(self.chemicals, self.X):
                if chemical.kind == "reactant":
                    chemical.mass = x/chemical.concentration
                else:
                    chemical.mass = x
        except Exception as e:
            raise e
        else:
            self.calculated = True

    def calculate_moles(self):
        '''
        Calculate the composition matrix by multiplying C = B * X
        '''

        if len(self.components) == 0:
            raise ValueError("No Zeolite components selected")

        if len(self.chemicals) == 0:
            raise ValueError("No chemicals selected")

        for comp in self.components:
            temp = ctrl.get_chemicals(self.session, components=[comp])
            if len(set([t.id for t in temp]) & set([r.id for r in self.chemicals])) == 0:
                raise ValueError("some components need their sources: {0:s}".format(comp.name))

        masses = []
        for chemical in self.chemicals:
            if chemical.kind == "reactant":
                masses.append(chemical.mass*chemical.concentration)
            else:
                masses.append(chemical.mass)

        self.X = np.array(masses, dtype=float)
        self.B = self.get_B_matrix()

        try:
            self.A = np.dot(np.transpose(self.B), self.X)
            for comp, a in zip(self.components, self.A):
                comp.moles = a/comp.molwt
        except Exception as e:
            raise e
        else:
            self.calculated = True

    def get_A_matrix(self):
        '''
        Compose the [A] matrix with masses of zeolite components.
        '''

        return np.asarray([z.moles*z.molwt for z in self.components], dtype=float)

    def get_B_matrix(self):
        '''
        Construct and return the batch matrix [B].
        '''

        B = np.zeros((len(self.chemicals), len(self.components)), dtype=float)

        for i, chemical in enumerate(self.chemicals):
            comps = self.session.query(Batch, Component).\
                    filter(Batch.chemical_id == chemical.id).\
                    filter(Component.id == Batch.component_id).all()
            wfs = self.get_weight_fractions(i, comps)
            for j, comp in enumerate(self.components):
                for cid, wf in wfs:
                    if comp.id == cid:
                        B[i, j] = wf
        return B

    def get_weight_fractions(self, rindex, comps):
        '''
        Calculate the weight fractions corresponding to a specific reactant
        and coupled zolite componts.

        lower case "m": mass in grmas
        upper case "M": molecular weight [gram/mol]
        '''

        res = []

        if self.chemicals[rindex].kind == "mixture":
            for batch, comp in comps:
                res.append((comp.id, batch.coefficient))
            return res

        elif self.chemicals[rindex].kind == "solution":
            if len(comps) > 2:
                raise ValueError("cannot handle cases of zeoindexes > 2")

            rct = self.chemicals[rindex]

            h2o = self.session.query(Chemical).filter(Chemical.formula=="H2O").one()
            M_solv = h2o.molwt

            M_solu = rct.molwt

            if abs(rct.concentration - 1.0) > 0.0001:
                n_solu = M_solu*M_solv/(M_solv + (1.0-rct.concentration)*M_solu/rct.concentration)/M_solu
                n_solv = M_solu*M_solv/(M_solu + rct.concentration*M_solv/(1.0-rct.concentration))/M_solv
            else:
                n_solu = 1.0
                n_solv = 0.0

            masses = list()

            for batch, comp in comps:
                if comp.formula != "H2O":
                    masses.append(batch.coefficient*n_solu*comp.molwt)
                else:
                    masses.append((batch.coefficient*n_solu + n_solv)*comp.molwt)

            tot_mass = sum(masses)
            for batch, comp in comps:
                if comp.formula != "H2O":
                    res.append((comp.id, batch.coefficient*n_solu*comp.molwt/tot_mass))
                else:
                    res.append((comp.id, (batch.coefficient*n_solu + n_solv)*comp.molwt/tot_mass))
            return res

        elif self.chemicals[rindex].kind == "reactant":
            if len(comps) > 1:
                tot_mass = sum([b.coefficient*c.molwt for b, c in comps])
                for batch, comp in comps:
                    res.append((comp.id, batch.coefficient*comp.molwt/tot_mass))
            else:
                res.append((comps[0][1].id, 1.0))
            return res

        else:
            raise ValueError("Unknown chemical kind: {}".format(self.chemicals[rindex].kind))

    def rescale_all(self):
        '''
        Rescale all masses of chemicals by a `scale_all` factor.
        '''

        res = [s.mass/self.scale_all for s in self.chemicals]
        return res

    def rescale_to_chemical(self, chemical, desired_mass):
        '''
        Rescale all masses by a factor, so that the selected item has the mass
        specified by the user.
        '''

        self.item_scale = chemical.mass/float(desired_mass)
        res = [s.mass/self.item_scale for s in self.chemicals]
        return res


    def rescale_to_sample(self, selected):
        '''
        Rescale all masses by a factor chosen in such a way that the sum of
        masses of a selected subset of chemicals is equal to the chosen sample
        size.
        '''

        self.sample_scale = sum([s.mass for s in selected])/float(self.sample_size)
        res = [s.mass/self.sample_scale for s in self.chemicals]
        return res

    def rescale_to_item(self, component, desired_moles):
        '''
        Rescale all mole numbers by a factor chosen in such a way that the
        selected *item* has th number of moles equal to *amount*.
        '''

        self.item_scale = component.moles/desired_moles
        res = [s.moles/self.item_scale for s in self.components]
        return res

    def print_A(self):
        '''
        Print the components vector in a readable form.
        '''

        width = max([len(c.listctrl_label()) for c in self.components] + [_MINWIDTH])
        print "\n     {0:*^{w}s}\n".format("  "+ "Composition Vector [C]" +"  ", w=width+34)
        print " "*5 + "{l:^{wl}}  |{mol:^15s}|{mas:^15s}".format(
                    l="Formula", wl=width, mol="Moles", mas="Mass [g]")
        print " "*5 + "-"*(width+4+30)
        for comp in self.components:
            print " "*5+"{l:>{wl}}  |{mol:>15.4f}|{mas:>15.4f}".format(
                    l=comp.listctrl_label(), wl=width, mol=comp.moles, mas=comp.mass)

    def print_batch_matrix(self):
        '''
        Print the batch matrix in a readable form.
        '''

        lr = len(self.chemicals)

        rowwidth = max([len(c.listctrl_label()) for c in self.components] + [_MINWIDTH])
        colwidth = max([len(r.listctrl_label()) for r in self.chemicals] + [_MINWIDTH])

        print "\n{0}{1:*^{w}s}\n".format(" "*7, "  Batch Matrix [B]  ", w=(colwidth+1)*lr+rowwidth)
        print "{}".format(" "*(8+rowwidth))+"|".join(["{0:^{cw}s}".format(c.listctrl_label(), cw=colwidth) for c in self.components])
        print "{}".format(" "*(7+rowwidth))+"{}".format("-"*(colwidth+1)*lr)
        for reac, row in zip(self.chemicals, self.B):
            print "     {0:>{w}s}  |".format(reac.listctrl_label(), w=rowwidth)+"|".join("{0:>{w}.4f}    ".format(x, w=colwidth-4) for x in row)

    def parse_formulas(self, string, delimiter=':'):
        '''
        Parse a string corresponding to the zeolite composition into a list of
        2-tuples.
        '''

        cre = re.compile(r'(?P<nmol>(-?\d+\.\d+|-?\d+))?\s*(?P<formula>[A-Za-z0-9\(\)]+)')
        result = []
        for comp in string.replace(" ", "").split(delimiter):
            m = cre.match(comp)
            if m:
                if m.group('nmol') is None:
                    nmol = 1.0
                else:
                    nmol = float(m.group('nmol'))
                result.append((m.group('formula'), nmol))
        return result
