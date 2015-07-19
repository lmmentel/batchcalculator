# file: utils.py
#
# -* -coding: utf-8 -*-
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

from collections import OrderedDict
from ObjectListView import ColumnDefn

__version__ = "0.2.1"

def format_float(item):
    '''Convert a float to string or None to empty string'''

    if item is not None:
        return "{0:7.3f}".format(item)
    else:
        return ""

COLUMNS = OrderedDict([
    ("cas"     , {"title" : "CAS No.",          "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "cas", "isEditable" : False}),
    ("category", {"title" : "Category",         "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "category", "isEditable" : False}),
    ("categobj", {"title" : "Category",         "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "name", "isEditable" : False}),
    ("chemical", {"title" : "Chemical",         "minimumWidth" : 150, "width" : 200, "align" : "left",  "valueGetter" : "chemical", "isEditable" : False, "isSpaceFilling" : True}),
    ("coeff"   , {"title" : "Coefficient",      "minimumWidth" : 100, "width" : 100, "align" : "right", "valueGetter" : "coefficient", "isEditable" : False, "stringConverter" : "%.2f"}),
    ("component",{"title" : "Chemical",         "minimumWidth" : 150, "width" : 200, "align" : "left",  "valueGetter" : "component", "isEditable" : False, "isSpaceFilling" : True}),
    ("conc"    , {"title" : "Concentration",    "minimumWidth" : 110, "width" : 110, "align" : "right", "valueGetter" : "concentration", "isEditable" : True, "stringConverter" : "%.2f"}),
    ("density" , {"title" : "Density",          "minimumWidth" : 120, "width" : 120, "align" : "right", "valueGetter" : "density", "isEditable" : False, "stringConverter" : format_float}),
    ("descr"   , {"title" : "Description",      "minimumWidth" : 200, "width" : 200, "align" : "left",  "valueGetter" : "description", "isEditable" : False}),
    ("elect"   , {"title" : "Electrolyte",      "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "electrolyte", "isEditable" : False, "isSpaceFilling" : True}),
    ("formula" , {"title" : "Formula",          "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "formula", "isEditable" : False, "isSpaceFilling" : True}),
    ("id"      , {"title" : "Id",               "minimumWidth" : 50,  "width" : 50,  "align" : "left",  "valueGetter" : "id", "isEditable" : False}),
    ("kind"    , {"title" : "Kind",             "minimumWidth" : 100, "width" : 100, "align" : "left",  "valueGetter" : "kind", "isEditable" : False}),
    ("label"   , {"title" : "Label",            "minimumWidth" : 100, "width" : 100, "align" : "left",  "valueGetter" : "listctrl_label", "isEditable" : False, "isSpaceFilling" : True}),
    ("laborant", {"title" : "Laborant",         "minimumWidth" : 100, "width" : 100, "align" : "left",  "valueGetter" : "laborant", "isEditable" : False, "isSpaceFilling" : False}),
    ("mass"    , {"title" : "Mass [g]",         "minimumWidth" : 100, "width" : 100, "align" : "right", "valueGetter" : "mass", "isEditable" : False, "stringConverter" : "%.4f"}),
    ("moles"   , {"title" : "Moles",            "minimumWidth" : 100, "width" : 100, "align" : "right", "valueGetter" : "moles", "isEditable" : True, "stringConverter" : "%.4f"}),
    ("molwt"   , {"title" : "Molecular Weight", "minimumWidth" : 120, "width" : 120, "align" : "right", "valueGetter" : "molwt", "isEditable" : False, "stringConverter" : "%.4f"}),
    ("name"    , {"title" : "Name",             "minimumWidth" : 200, "width" : 200, "align" : "left",  "valueGetter" : "name", "isEditable" : False, "isSpaceFilling" : True}),
    ("pk"      , {"title" : "pK",               "minimumWidth" : 100, "width" : 120, "align" : "right", "valueGetter" : "pk", "isEditable" : False, "stringConverter" : format_float}),
    ("physform", {"title" : "Physical Form",    "minimumWidth" : 150, "width" : 150, "align" : "left",  "valueGetter" : "physical_form", "isEditable" : False}),
    ("reaction", {"title" : "Reaction",         "minimumWidth" : 200, "width" : 200, "align" : "left",  "valueGetter" : "reaction", "isEditable" : False, "isSpaceFilling" : True}),
    ("reference", {"title" : "Reference",       "minimumWidth" : 200, "width" : 200, "align" : "left",  "valueGetter" : "reference", "isEditable" : False}),
    ("scaled"  , {"title" : "Scaled Mass [g]",  "minimumWidth" : 140, "width" : 140, "align" : "right", "valueGetter" : "mass", "isEditable" : False, "stringConverter" : "%.4f"}),
    ("short"   , {"title" : "Short name",       "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "short_name", "isEditable" : False}),
    ("smiles"  , {"title" : "SMILES",           "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "smiles", "isEditable" : False}),
    ("target"  , {"title" : "Target Material",  "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "target_material", "isEditable" : False}),
    ("temperature", {"title" : "Temperature",   "minimumWidth" : 120, "width" : 120, "align" : "right", "valueGetter" : "temperature", "isEditable" : False, "stringConverter" : "%.1f"}),
    ("volume"  , {"title" : "Volume [cm3]",     "minimumWidth" : 120, "width" : 120, "align" : "right", "valueGetter" : "volume", "isEditable" : False, "stringConverter" : format_float}),
])

def get_columns(cols):
    '''
    Return list of ColumnDefn objects based on the definitions in COLUMNS

    Args:
        cols : list of str
            list of keys from COLUMNS dict
    '''

    return [ColumnDefn(**COLUMNS[col]) for col in cols]

