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

__version__ = "0.1.2"

import operator
import os
import re
import sys

from numpy.linalg import solve, lstsq
import numpy as np

from sqlalchemy import orm, Column, Integer, String, Float, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

_minwidth = 15

Base = declarative_base()

class BaseChemical(object):

    def formula_to_tex(self):
        '''
        Convert the formula string to tex string.
        '''
        return re.sub(ur'(\d+)', ur'$_{\1}$', self.formula)

    def formula_to_html(self):
        '''
        Convert the formula string to html string.
        '''
        return re.sub(ur'(\d+)', ur'<sub>\1</sub>', self.formula)

    def listctrl_label(self):
        '''
        Return the string to be displayed in the ListCtrl's.
        '''
        if self.is_undefined(self.short_name):
            res = self.name
        else:
            res = self.short_name
        return res

    def html_label(self):
        '''
        Return a label to be used in printable tables in html format.
        '''
        if self.is_undefined(self.short_name):
            res = self.formula_to_html()
        else:
            res = self.short_name
        return res

    def tex_label(self):
        '''
        Return a label to be used in printable tables in tex format.
        '''
        if self.is_undefined(self.short_name):
            res = self.formula_to_tex()
        else:
            res = self.short_name
        return res

    @staticmethod
    def is_undefined(item):
        if item is None or item.lower() in ["", "null", "none"]:
            return True
        else:
            return False

class Category(Base):
    __tablename__ = 'categories'

    id        = Column(Integer, primary_key=True)
    name      = Column(String, nullable=False)
    full_name = Column(String)

    def __repr__(self):
        return "<Category(id={i}, name={n}, full_name={f})>".format(i=self.id,
                n=self.name, f=self.full_name)

class Electrolyte(Base):
    __tablename__ = 'electrolytes'

    id   = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<Electrolyte(id={i}, form={n})>".format(i=self.id, n=self.name)

class PhysicalForm(Base):
    __tablename__ = 'physical_forms'

    id   = Column(Integer, primary_key=True)
    form = Column(String, nullable=False)

    def __repr__(self):
        return "<PhysicalForm(id={i}, form={n})>".format(i=self.id, n=self.form)

class Kind(Base):
    __tablename__ = 'kinds'

    id   = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<Kind(id={i}, name={n})>".format(i=self.id, n=self.name)

class Reaction(Base):
    __tablename__ = 'reactions'

    id       = Column(Integer, primary_key=True)
    reaction = Column(String, nullable=False)

    def __repr__(self):
        return "<Reaction(id={i}, reaction={n})>".format(i=self.id, n=self.reaction)

class Batch(Base):
    __tablename__ = 'batch'

    id           = Column(Integer, primary_key=True)
    chemical_id  = Column(Integer, ForeignKey('chemicals.id'), nullable=False)
    component_id = Column(Integer, ForeignKey('components.id'), nullable=False)
    reaction_id  = Column(Integer, ForeignKey('reactions.id'), nullable=True)
    coefficient  = Column(Float, nullable=True)

    _chemical = relationship("Chemical")
    chemical = association_proxy("_chemical", "name")
    _component = relationship("Component")
    component = association_proxy("_component", "name")
    _reaction= relationship("Reaction")
    reaction = association_proxy("_reaction", "reaction")

    def __repr__(self):
        return "<Batch(id={i:>2d}, chemical_id='{n:>5d}', component_id='{z:>5d}', coefficient={c:8.2f})>".format(
                i=self.id, n=self.chemical_id, z=self.component_id, c=self.coefficient)

class Component(BaseChemical, Base):
    '''
    Class representing the Component object. The component can belong to one of
    the 3 categories:
        * Zeolite component
        * Template
        * Zeolite Growth Modifier
    '''
    __tablename__ = 'components'

    id          = Column(Integer, primary_key=True)
    name        = Column(String, nullable=False)
    formula     = Column(String, nullable=False)
    molwt       = Column(Float, nullable=False)
    short_name  = Column(String)

    _category_id = Column("category_id", Integer, ForeignKey('categories.id'))
    _category = relationship("Category")
    category = association_proxy("_category", "name")

    @orm.reconstructor
    def init_on_load(self):
        self.moles = 0.0

    @hybrid_property
    def mass(self):
        return self.moles*self.molwt

    def __repr__(self):
        return "<Component(id={i:>2d}, name='{n:s}', formula='{f:s}')>".format(
                i=self.id, n=self.name, f=self.formula)

class Chemical(BaseChemical, Base):
    '''
    Class representing the Chemical object, (off the shelf reactants).
    '''
    __tablename__ = 'chemicals'

    id            = Column(Integer, primary_key=True)
    name          = Column(String, nullable=False)
    formula       = Column(String, nullable=False)
    molwt         = Column(Float, nullable=False)
    short_name    = Column(String)
    concentration = Column(Float)
    cas           = Column(String)
    density       = Column(Float)
    pk            = Column(Float)
    smiles        = Column(String)

    _kind_id       = Column("kind_id", Integer, ForeignKey('kinds.id'), nullable=False)
    _kind = relationship("Kind")
    kind = association_proxy("_kind", "name")

    _electrolyte_id = Column("electrolyte_id", Integer, ForeignKey('electrolytes.id'))
    _electrolyte = relationship("Electrolyte")
    electrolyte = association_proxy("_electrolyte", "name")

    _physical_form_id = Column("physical_form_id", Integer, ForeignKey('physical_forms.id'))
    _physical_form = relationship("PhysicalForm")
    physical_form = association_proxy("_physical_form", "form")

    @orm.reconstructor
    def init_on_load(self):
        self.mass = 0.0

    @hybrid_property
    def moles(self):
        return self.mass/self.molwt

    @hybrid_property
    def volume(self):
        if self.density is not None and self.physical_form == "liquid":
            return self.mass/self.density
        else:
            return None

    def html_label(self):
        '''
        Return a label to be used in printable tables in html format.
        '''
        if self.is_undefined(self.short_name):
            res = self.formula_to_html() + u" ({0:>4.1f}%)".format(100*self.concentration)
        else:
            res = self.short_name + u" ({0:>4.1f}%)".format(100*self.concentration)
        return res

    def tex_label(self):
        '''
        Return a label to be used in printable tables in tex format.
        '''
        if self.is_undefined(self.short_name):
            res = self.formula_to_tex() + u" ({0:>4.1f}\%)".format(100*self.concentration)
        else:
            res = self.short_name + u" ({0:>4.1f}\%)".format(100*self.concentration)
        return res

    def __repr__(self):
        #return "<Chemical(id={i:>2d}, name='{n:s}', formula='{f:s}')>".format(
        #        i=self.id, n=self.name, f=self.formula)
        return "%s(\n%s)" % (
                 (self.__class__.__name__),
                 ', '.join(["%s=%r\n" % (key, getattr(self, key))
                            for key in sorted(self.__dict__.keys())
                            if not key.startswith('_')]))

class BatchCalculator(object):

    def __init__(self):

        # default database path
        dbpath = self.get_dbpath()
        self.new_dbsession(dbpath)

        self.lists = ["components", "chemicals"]

        # create lists for different categories of
        for lst in self.lists:
            setattr(self, lst, list())

        self.calculated = False

        self.A = list()
        self.B = list()
        self.X = list()

        self.scale_all = 100.0
        self.sample_scale = 1.0
        self.sample_size = 5.0
        self.item_scale = None
        self.selections = []

    def get_dbpath(self):
        '''
        Depending on the execution environment get the proper database path.
        '''

        dbpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data", "zeolite.db")
        if os.path.exists(dbpath):
            return dbpath
        elif sys.executable is not None:
            dbpath = os.path.join(os.path.dirname(sys.executable), "data", "zeolite.db")
            return dbpath
        else:
            raise ValueError("database not found on: {}".format(dbpath))

    def new_dbsession(self, dbpath):
        '''
        When the new database is chosen, close the old session and establish a new
        one.
        '''

        if hasattr(self, "session"):
            self.session.close()
        engine = create_engine("sqlite:///{path:s}".format(path=dbpath), echo=True)
        DBSession  = sessionmaker(bind=engine)
        self.session = DBSession()

    def reset(self):
        '''
        Clear the state of the calculation by reseting all the list and
        variables.
        '''

        self.calculated = False

        self.components = []
        self.chemicals = []

        self.A = []
        self.B = []
        self.X = []

        self.scale_all = 100.0
        self.sample_scale = 1.0
        self.sample_size = 5.0
        self.item_scale = None
        self.selections = []

    def get_batch_records(self):

        query = self.session.query(Batch).order_by(Batch.id).all()
        return query

    def get_components(self):

        query = self.session.query(Component).order_by(Component.id).all()
        return query

    def get_chemicals(self, showall=False):
        '''
        Return chemicals that are sources for the components present in the
        components list, of the list is empty return all the components.
        '''

        if showall:
            query =  self.session.query(Chemical).order_by(Chemical.id).all()
        else:
            compset = set()
            for comp in self.components:
                temp = self.session.query(Chemical).join(Batch).\
                            filter(Batch.component_id == comp.id).all()
                compset.update(temp)
                query = sorted(list(compset), key=lambda x: x.id)
        return query

    def get_categories(self):
        '''
        Return the list of `Category` objects from the database
        '''
        return self.session.query(Category).order_by(Category.id).all()

    def get_kinds(self):
        '''
        Return the list of `Kind` objects from the database
        '''
        return self.session.query(Kind).order_by(Kind.id).all()

    def get_reactions(self):
        '''
        Return the list of `Reaction` objects from the database
        '''
        return self.session.query(Reaction).order_by(Reaction.id).all()

    def get_physical_forms(self):
        '''
        Return the list of `PhysicalForm` objects from the database
        '''
        return self.session.query(PhysicalForm).order_by(PhysicalForm.id).all()

    def get_electrolytes(self):
        '''
        Return the list of `Electrolyte` objects from the database
        '''
        return self.session.query(Electrolyte).order_by(Electrolyte.id).all()

    @staticmethod
    def is_empty(item):
        if item is None or item in ["", "NULL", "None"]:
            return True
        else:
            return False

    def select_item(self, lst, attr, value):
        '''
        From a list of objects "lst" having a common attribute get the index of the
        object having the attribute "attr" set to "value".
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
            tempr = self.session.query(Chemical).join(Batch).filter(Batch.component_id == comp.id).all()
            if len(set([t.id for t in tempr]) & set([r.id for r in self.chemicals])) == 0:
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
            tempr = self.session.query(Chemical).join(Batch).filter(Batch.component_id == comp.id).all()
            if len(set([t.id for t in tempr]) & set([r.id for r in self.chemicals])) == 0:
                raise ValueError("some compoennts need their sources: {0:s}".format(comp.name))

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

        item_scale = chemical.mass/float(desired_mass)
        res = [s.mass/item_scale for s in self.chemicals]
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

        self.item_scale = desired_moles/component.moles
        res = [s.moles*self.item_scale for s in self.components]
        return res

    def print_A(self):
        '''
        Print the components vector in a readable form.
        '''

        width = max([len(c.listctrl_label()) for c in self.components] + [_minwidth])
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

        rowwidth = max([len(c.listctrl_label()) for c in self.components] + [_minwidth])
        colwidth = max([len(r.listctrl_label()) for r in self.chemicals] + [_minwidth])

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
