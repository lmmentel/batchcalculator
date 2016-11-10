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


import re

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

__version__ = "0.3.0"

Base = declarative_base()


class ObjRepr(object):

    def __repr__(self):
        return "%s(\n%s)" % (
               (self.__class__.__name__),
               ' '.join(["\t%s=%r,\n" % (key, getattr(self, key))
                         for key in sorted(self.__dict__.keys())
                         if not key.startswith('_')]))


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
        '''
        Return True if the item is undefined, False otherwise.
        '''
        if item is None or item.lower() in ["", "null", "none"]:
            return True
        else:
            return False

    def __repr__(self):
        return "%s(\n%s)" % (
               (self.__class__.__name__),
               ' '.join(["\t%s=%r,\n" % (key, getattr(self, key))
                         for key in sorted(self.__dict__.keys())
                         if not key.startswith('_')]))


class Synthesis(ObjRepr, Base):
    '''
    Synthesis object

    Attributes
    ----------
    name : str
        Name of the synthesis (label)
    reference : str
        Literature reference
    laborant : str
        Name of the person performing the synthesis (or initials)
    temperature : float
        Temperature in degrees Celsius
    crystallization_time : float
        Crystallization time in hours
    oven_type : str
        Type of the oven used
    target_material : str
        In case of zeolites it should be the three letter framework code
    description : str
        Description of the synthesis
    strirring : str
        Stirring
    '''

    __tablename__ = "synthesis"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    reference = Column(String)
    laborant = Column(String)
    temperature = Column(Float)
    crystallization_time = Column(Float)
    oven_type = Column(String)
    target_material = Column(String)
    description = Column(String)
    stirring = Column(String)

    components = relationship("SynthesisComponent")
    chemicals = relationship("SynthesisChemical")


class SynthesisChemical(ObjRepr, Base):
    __tablename__ = "synthesischemicals"

    id = Column(Integer, primary_key=True)
    synthesis_id = Column(Integer, ForeignKey("synthesis.id"))
    chemical_id = Column(Integer, ForeignKey("chemicals.id"))
    chemical = relationship("Chemical")
    mass = Column(Float, nullable=False)


class SynthesisComponent(ObjRepr, Base):
    __tablename__ = "synthesiscomponents"

    id = Column(Integer, primary_key=True)
    synthesis_id = Column(Integer, ForeignKey("synthesis.id"))
    component_id = Column(Integer, ForeignKey("components.id"))
    component = relationship("Component")
    moles = Column(Float, nullable=False)


class SEMimage(ObjRepr, Base):
    __tablename__ = "semimages"

    id = Column(Integer, primary_key=True)
    synthesis_id = Column(Integer, ForeignKey("synthesis.id"))
    name = Column(String)


class Category(ObjRepr, Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    full_name = Column(String)


class Electrolyte(ObjRepr, Base):
    __tablename__ = 'electrolytes'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class PhysicalForm(ObjRepr, Base):
    __tablename__ = 'physical_forms'

    id = Column(Integer, primary_key=True)
    form = Column(String, nullable=False)


class Kind(Base):
    '''
    Kind object

    Attributes
    ----------
    name : str
        Kind of the chemical determining how the weight fraction will be
        calculated. The allowed values are:
            "mixture"  - weight mixture
            "reactant" - general reactant
            "solution" - water solution given
    '''

    __tablename__ = 'kinds'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<Kind(id={i}, name={n})>".format(i=self.id, n=self.name)


class Reaction(Base):
    '''
    Reaction object

    Attributes
    ----------
    reaction : str
        Reaction relating chemicals to components
    '''

    __tablename__ = 'reactions'

    id = Column(Integer, primary_key=True)
    reaction = Column(String, nullable=False)

    def __repr__(self):
        return "<Reaction(id={i}, reaction={n})>".format(i=self.id,
                                                         n=self.reaction)


class Batch(Base):
    '''
    Batch object

    Attributes
    ----------
    chemical_id : int
        Id number of the Chemical from the chemicals table
    component_id : int
        Id number of the Component from the components table
    reaction_id : int
        Id number of the Reaction from the reactions table
    coefficient : float
        Stechimetric coefficient relating the chemical to the component per 1
        mole of chemical
    '''

    __tablename__ = 'batch'

    id = Column(Integer, primary_key=True)
    chemical_id = Column(Integer, ForeignKey('chemicals.id'), nullable=False)
    component_id = Column(Integer, ForeignKey('components.id'), nullable=False)
    reaction_id = Column(Integer, ForeignKey('reactions.id'), nullable=True)
    coefficient = Column(Float, nullable=True)

    _chemical = relationship("Chemical")
    chemical = association_proxy("_chemical", "name")
    _component = relationship("Component")
    component = association_proxy("_component", "name")
    _reaction = relationship("Reaction")
    reaction = association_proxy("_reaction", "reaction")

    def __repr__(self):
        return "<Batch(id={i:>2d}, chemical_id='{n:>5d}', component_id='{z:>5d}', coefficient={c:8.2f})>".format(
                i=self.id, n=self.chemical_id, z=self.component_id, c=self.coefficient)


class Component(BaseChemical, Base):
    '''
    Component object

    Attributes
    ----------
    name : str
        Name of the component
    formula : str
        Chemical formula
    molwt : float
        Molecular weight
    short_name : str
        Short name
    _category : int
        Id number of the Category from the categories table
    '''

    __tablename__ = 'components'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    formula = Column(String, nullable=False)
    molwt = Column(Float, nullable=False)
    short_name = Column(String)

    _category_id = Column("category_id", Integer, ForeignKey('categories.id'))
    _category = relationship("Category")
    category = association_proxy("_category", "name")

    @reconstructor
    def init_on_load(self):
        self.moles = 1.0

    @hybrid_property
    def mass(self):
        '''
        Return mass calculated from number of moles and molecular weight.
        '''
        return self.moles * self.molwt


class Chemical(BaseChemical, Base):
    '''
    Chemical object

    Attributes
    ----------
    name : str
        Name of the chemical
    formula : str
        Chemical formula
    molwt : float
        Molecular weight
    short_name : str
        Short name
    concentration : float
        Concentration as weight percent
    cas : str
        CAS number
    density : float
        Density in g/cm^3
    pk : float
        pK value
    smiles : str
        SMILES formula
    '''
    __tablename__ = 'chemicals'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    formula = Column(String, nullable=False)
    molwt = Column(Float, nullable=False)
    short_name = Column(String)
    concentration = Column(Float)
    cas = Column(String)
    density = Column(Float)
    pk = Column(Float)
    smiles = Column(String)

    _kind_id = Column("kind_id", Integer, ForeignKey('kinds.id'), nullable=False)
    _kind = relationship("Kind")
    kind = association_proxy("_kind", "name")

    _electrolyte_id = Column("electrolyte_id", Integer, ForeignKey('electrolytes.id'))
    _electrolyte = relationship("Electrolyte")
    electrolyte = association_proxy("_electrolyte", "name")

    _physical_form_id = Column("physical_form_id", Integer, ForeignKey('physical_forms.id'))
    _physical_form = relationship("PhysicalForm")
    physical_form = association_proxy("_physical_form", "form")

    @reconstructor
    def init_on_load(self):
        self.mass = 0.0

    @hybrid_property
    def moles(self):
        '''
        Return number of moles calculated from mass and molecular weight.
        '''
        return self.mass / self.molwt

    @hybrid_property
    def volume(self):
        '''
        Return volume calculated from mass and density if chemical is a liquid.
        '''
        if self.density is not None and self.physical_form == "liquid":
            return self.mass / self.density
        else:
            return None

    def html_label(self):
        '''
        Return a label to be used in printable tables in html format.
        '''
        if self.is_undefined(self.short_name):
            res = self.formula_to_html() + u" ({0:>4.1f}%)".format(100.0 * self.concentration)
        else:
            res = self.short_name + u" ({0:>4.1f}%)".format(100.0 * self.concentration)
        return res

    def tex_label(self):
        '''
        Return a label to be used in printable tables in tex format.
        '''
        if self.is_undefined(self.short_name):
            res = self.formula_to_tex() + u" ({0:>4.1f}\%)".format(100.0 * self.concentration)
        else:
            res = self.short_name + u" ({0:>4.1f}\%)".format(100.0 * self.concentration)
        return res
