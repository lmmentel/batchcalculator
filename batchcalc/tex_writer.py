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

from __future__ import print_function, unicode_literals

import os
import sys
import datetime
from jinja2 import Environment, FileSystemLoader

__version__ = "0.3.0"


def get_temppath():
    '''
    Depending on the execution environment get the proper template path.
    '''

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        "templates", "tex")
    if os.path.exists(path):
        return path
    elif sys.executable is not None:
        path = os.path.join(os.path.dirname(sys.executable),
                            "templates", "tex")
        return path
    else:
        raise ValueError("template path doesn't exist: {}".format(path))


def get_report_as_string(flags, model):
    '''
    Return a string with a report in the TeX format.
    '''

    env = Environment('<*', '*>', '<<', '>>', '<#', '#>',
                      autoescape=False,
                      extensions=['jinja2.ext.autoescape'],
                      loader=FileSystemLoader(get_temppath()))
    template = env.get_template('report_color.tex')

    flags['date'] = datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")
    flags['molar_ratios'] = r':'.join(['{0}{1}'.format(x.moles, x.tex_label()) for x in model.components])

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
    if flags['comment'] != "":
        flags['comment_on'] = True

    tex = template.render(flags)
    return tex


def tex_A(model):

    tshape = u'{l' + u'R' * len(model.components) + u'}'
    table = r'\begin{center}'+u'\n'+r'\begin{tabularx}{\textwidth}'+tshape+r'\toprule'+u'\n'
    table += u'Compound &' + ' & '.join([r'\multicolumn{1}{c}{'+c.tex_label()+r'}' for c in model.components]) + r'\\ \midrule' + u'\n'
    table += u'Mole ratio &' + ' & '.join(["{0:10.3f}".format(c.moles) for c in model.components]) + r'\\ ' + u'\n'
    table += u'Weight [g] &' + ' & '.join(["{0:10.3f}".format(c.mass) for c in model.components]) + r'\\ ' + u'\n'
    table += u'Mol. wt. [g/mol] &' + ' & '.join(["{0:10.3f}".format(c.molwt) for c in model.components]) + r'\\ ' + u'\n'
    return table + r'\bottomrule\end{tabularx}'+u'\n'+r'\end{center}'+u'\n'


def tex_B(model):

    tshape = u'{l'+u'C'*len(model.components)+u'}'
    table = r'\begin{center}'+u'\n'+r'\begin{tabularx}{\textwidth}'+tshape+r'\toprule'+u'\n'
    table += u'Compound' + u' & ' + u' & '.join([z.tex_label() for z in model.components]) + r'\\ \midrule' + u'\n'
    for reactant, row in zip(model.chemicals, model.B):
        table += reactant.tex_label() + u' & ' + u' & '.join(["{0:10.4f}".format(x) for x in row]) + r'\\' + u'\n'
    return table + r'\bottomrule\end{tabularx}'+u'\n'+r'\end{center}'+u'\n'


def tex_X(model):

    masssum = sum([s.mass for s in model.chemicals])

    table = r'\begin{center}'+u'\n'+r'\begin{tabularx}{\textwidth}{lRR|C|}\toprule'+u'\n'
    table += " & ".join([r'Substance', r'\multicolumn{1}{c}{Mass [g]}',
                         r'Scaled Mass [g]',
                         r'Weighted mass [g]']) + r'\\ \midrule' + u'\n'
    for i, subs in enumerate(model.chemicals, start=1):
        table += r"{l:>20s} & {v:>15.4f} & {s:>15.4f} & \\".format(
                    l=subs.tex_label(), v=subs.mass, s=subs.mass/model.scale_all)
        if i < len(model.chemicals):
            table += r'\cline{4-4}' + u'\n'
        else:
            table += u'\n'
    table += r'\midrule Sum & '+ "{0:>15.4f}".format(masssum) + ' & ' +\
             "{0:>15.4f}".format(masssum/model.scale_all) + r' & \\ ' + u'\n'
    return table + r'\bottomrule\end{tabularx}'+u'\n'+r'\end{center}'+u'\n'


def tex_X_rescale(model):

    masspar = sum([s.mass for s in model.selections])
    masssum = sum([s.mass for s in model.chemicals])

    table = r'\begin{center}'+u'\n'+r'\begin{tabularx}{\textwidth}{lRR|C|}\toprule'+u'\n'
    table += " & ".join([r'Substance', r'\multicolumn{1}{c}{Mass [g]}',
                         r'Scaled Mass [g]',
                         r'Weighted mass [g]']) + r'\\ \midrule' + u'\n'
    for i, subs in enumerate(model.selections, start=1):
        table += r"{l:>20s} & {v:>15.4f} & {s:>15.4f} & \\".format(l=subs.tex_label(), v=subs.mass, s=subs.mass/model.sample_scale)
        if i < len(model.selections):
            table += r'\cline{4-4}' + u'\n'
        else:
            table += u'\n'
    table += r'\midrule Sum & '+ "{0:>15.4f}".format(masspar) + ' & ' + "{0:>15.4f}".format(masspar/model.sample_scale) + r' & \\ '
    nsel_ids = set([x.id for x in model.chemicals]).difference(set([x.id for x in model.selections]))
    not_selected = [x for x in model.chemicals if x.id in nsel_ids]
    if len(not_selected) > 0:
        table += r'\midrule' + u'\n'
    for i, subs in enumerate(not_selected, start=1):
            table += r"{l:>20s} & {v:>15.4f} & {s:>15.4f} & \\ ".format(l=subs.tex_label(), v=subs.mass, s=subs.mass/model.sample_scale)
            if i < len(not_selected):
                table += r'\cline{4-4}' + u'\n'
            else:
                table += u'\n'
    table += r'\midrule Total Sum & '+ "{0:>15.4f}".format(masssum) + ' & ' + "{0:>15.4f}".format(masssum/model.sample_scale) + r' & \\ '
    return table + r'\bottomrule\end{tabularx}'+u'\n'+r'\end{center}'+u'\n'
