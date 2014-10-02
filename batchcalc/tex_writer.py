# -*- coding: utf-8 -*-
#
#    Zeolite Batch Calculator
#
# A program based for calculating the correct amount of reagents (batch) for a
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

__version__ = "0.1.0"

import re
import os
import datetime
import numpy as np
from jinja2 import Environment, PackageLoader, Template

def get_report_as_string(flags, model):
    '''
    Return a string with a report in the TeX format.
    '''

    env = Environment('<*', '*>', '<<', '>>', '<#', '#>',
                    autoescape=False,
                    extensions=['jinja2.ext.autoescape'],
                    loader=PackageLoader('batchcalc', os.path.join('templates', 'tex')))
    template = env.get_template('report_color.tex')

    flags['date'] = datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")
    flags['molar_ratios'] = ur':'.join(['{0}{1}'.format(x.moles, x.label()) for x in model.components])

    if flags["composition"]:
        flags['a_matrix'] = tex_A(model)
    if flags["batch"]:
        flags['b_matrix'] = tex_B(model)
    if flags["rescale_all"]:
        flags['rescale_all_factor'] = u'{0:8.4f}'.format(model.scale_all)
        flags['x_matrix'] = tex_X(model)
    if flags["rescale_to"]:
        flags['rescale_to_factor'] = u'{0:8.4f}'.format(model.sample_scale)
        flags['x_matrix_scaled'] = tex_X_rescale(model)

    tex = template.render(flags)
    return tex

def tex_A(model):

    tshape = u'{l|'+u'R'*len(model.components)+u'}'
    table = ur'\begin{center}'+u'\n'+ur'\begin{tabularx}{\textwidth}'+tshape+ur'\toprule'+u'\n'
    table += u'Compound &' + ' & '.join([ur'\multicolumn{1}{c}{'+c.label()+ur'}' for c in model.components]) + ur'\\ \midrule' + u'\n'
    table += u'Mole ratio &' + ' & '.join(["{0:10.3f}".format(c.moles) for c in model.components]) + ur'\\ ' + u'\n'
    table += u'Weight [g] &' + ' & '.join(["{0:10.3f}".format(c.mass) for c in model.components]) + ur'\\ ' + u'\n'
    table += u'Mol. wt. [g/mol] &' + ' & '.join(["{0:10.3f}".format(c.molwt) for c in model.components]) + ur'\\ ' + u'\n'
    return table + ur'\bottomrule\end{tabularx}'+u'\n'+ur'\end{center}'+u'\n'

def tex_B(model):

    tshape = u'{l'+u'C'*len(model.components)+u'}'
    table = ur'\begin{center}'+u'\n'+ur'\begin{tabularx}{\textwidth}'+tshape+ur'\toprule'+u'\n'
    table += u'Compound' + u' & ' + u' & '.join([z.label() for z in model.components]) + ur'\\ \midrule' + u'\n'
    for reactant, row in zip(model.reactants, model.B):
        table += reactant.label() + u' & ' + u' & '.join(["{0:10.4f}".format(x) for x in row]) + ur'\\' + u'\n'
    return table + ur'\bottomrule\end{tabularx}'+u'\n'+ur'\end{center}'+u'\n'

def tex_X(model):

    masssum = sum([s.mass for s in model.reactants])

    table = ur'\begin{center}'+u'\n'+ur'\begin{tabularx}{\textwidth}{lRR|C|}\toprule'+u'\n'
    table += " & ".join([ur'Substance', ur'\multicolumn{1}{c}{Mass [g]}',
                         ur'Scaled Mass [g] ({0:8.3f})'.format(model.scale_all),
                         ur'Weighted mass [g]']) + ur'\\ \midrule' + u'\n'
    for i, subs in enumerate(model.reactants, start=1):
        table += ur"{l:>20s} & {v:>15.4f} & {s:>15.4f} & \\".format(
                    l=subs.label(), v=subs.mass, s=subs.mass/model.scale_all)
        if i < len(model.reactants):
            table += ur'\cline{4-4}' + u'\n'
        else:
            table += u'\n'
    table += ur'\midrule Sum & '+ "{0:>15.4f}".format(masssum) + ' & ' +\
             "{0:>15.4f}".format(masssum/model.scale_all) + ur' & \\ ' + u'\n'
    return table + ur'\bottomrule\end{tabularx}'+u'\n'+ur'\end{center}'+u'\n'

def tex_X_rescale(model):

    masssum = sum([s.mass for s in model.reactants])

    table = ur'\begin{center}'+u'\n'+ur'\begin{tabularx}{\textwidth}{lRR|C|}\toprule'+u'\n'
    table += " & ".join([ur'Substance', ur'\multicolumn{1}{c}{Mass [g]}',
                         ur'Scaled Mass [g] ({0:8.3f})'.format(model.sample_scale),
                         ur'Weighted mass [g]']) + ur'\\ \midrule' + u'\n'
    for i, idx in enumerate(model.selections, start=1):
        subs = model.reactants[idx]
        table += ur"{l:>20s} & {v:>15.4f} & {s:>15.4f} & \\".format(l=subs.label(), v=subs.mass, s=subs.mass/model.sample_scale)
        if i < len(model.selections):
            table += ur'\cline{4-4}' + u'\n'
        else:
            table += u'\n'
    table += ur'\midrule Sum & '+ "{0:>15.4f}".format(masssum) + ' & ' + "{0:>15.4f}".format(masssum/model.sample_scale) + ur' & \\ '
    not_selected = [model.reactants[idx] for idx in range(len(model.reactants)) if idx not in model.selections]
    if len(not_selected) > 0:
        table += ur'\midrule' + u'\n'
    for i, subs in enumerate(not_selected, start=1):
            table += ur"{l:>20s} & {v:>15.4f} & {s:>15.4f} & \\ ".format(l=subs.label(), v=subs.mass, s=subs.mass/model.sample_scale)
            if i < len(not_selected):
                table += ur'\cline{4-4}' + u'\n'
            else:
                table += u'\n'
    return table + ur'\bottomrule\end{tabularx}'+u'\n'+ur'\end{center}'+u'\n'
