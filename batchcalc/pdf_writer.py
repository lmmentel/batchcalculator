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

import datetime
import numpy as np
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import A4, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name='RightJ', alignment=TA_RIGHT))
styles.add(ParagraphStyle(name='BlueTitle', alignment=TA_CENTER, textColor=colors.blue, fontSize=22))
styles.add(ParagraphStyle(name='Section', textColor=colors.blue, fontSize=16))
styles.add(ParagraphStyle(name='Compo', alignment=TA_CENTER, textColor=colors.blue, fontSize=14))
styles.add(ParagraphStyle(name='CenterJ', alignment=TA_CENTER))

tab_style = TableStyle([
    ('FONT', (0, 0), (-1, -1), 'Helvetica'),
    ('FONT', (1, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('LINEABOVE', (0, 0), (-1, 1), 0.5, colors.black),
    ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black),
])

res_tab_style = TableStyle([
    ('FONT', (0, 0), (-1, -1), 'Helvetica'),
    ('FONT', (1, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('LINEABOVE', (0, 0), (-1, 1), 0.5, colors.black),
    ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ('LINEBELOW', (0, -2), (-1, -1), 0.5, colors.black),
    ('LINEBEFORE', (-1, 0), (-1, -1), 0.5, colors.black),
    ('LINEBELOW', (-1, 1), (-1, -1), 0.5, colors.black),
    ])

def create_header(model, title, author, email, no_moles=False):
    story = []
    date = datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")
    story.append(Paragraph(date, styles['RightJ']))
    story.append(Paragraph(title, styles['BlueTitle']))
    story.append(Spacer(1, 16))
    if no_moles:
        story.append(Paragraph(ur':'.join(['{0}'.format(x.html_label()) for x in model.components]), styles['Compo']))
    else:
        story.append(Paragraph(ur':'.join(['{0}{1}'.format(x.moles, x.html_label()) for x in model.components]), styles['Compo']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(author, styles['CenterJ']))
    story.append(Paragraph(email, styles['CenterJ']))
    return story

def chemicals_table(model):

    data = [['Chemical', 'Mass [g]', 'Concentration', 'Mol. wt. [g/mol]']]
    for chem in model.chemicals:
        data.append([chem.formula, "{0:10.4f}".format(chem.mass), "{0:10.4f}".format(chem.concentration), "{0:10.4f}".format(chem.molwt)])

    tab = Table(data)
    tab.setStyle(tab_style)
    return tab

def components_table(model, no_moles=False):

    if no_moles:
        data = [['Compound']+[c.formula for c in model.components],
                ['Weight [g]']+["{0:10.3f}".format(c.mass) for c in model.components],
                ['Mol. wt. [g/mol]']+["{0:10.3f}".format(c.molwt) for x in model.components]]
    else:
        data = [['Compound']+[c.formula for c in model.components],
                ['Mole ratio']+["{0:10.3f}".format(c.moles) for c in model.components],
                ['Weight [g]']+["{0:10.3f}".format(c.mass) for c in model.components],
                ['Mol. wt. [g/mol]']+["{0:10.3f}".format(c.molwt) for x in model.components]]

    tab = Table(data)
    tab.setStyle(tab_style)
    return tab

def composition_results_table(model):

    data = [['Component', 'Moles', 'Mass [g]']]
    for comp in model.components:
        data.append([comp.formula, "{0:10.4f}".format(comp.moles), "{0:10.4f}".format(comp.mass)])

    tab = Table(data)
    tab.setStyle(tab_style)
    return tab

def batch_table(model):

    temp = np.array(map(lambda x: "{0:8.4f}".format(x), model.get_B_matrix().reshape(model.B.size)))
    data = temp.reshape(model.get_B_matrix().shape).tolist()
    for row, chemical in zip(data, model.chemicals):
        row.insert(0, chemical.formula + " ({0:6.2f}%)".format(chemical.concentration*100))
    data.insert(0, ['Compound']+[c.formula for c in model.components])
    tab = Table(data)
    tab.setStyle(tab_style)
    return tab

def results_table(model):

    data = [["Substance", "Mass [g]", "Scaled Mass [g]", "Weighted Mass [g]"]]
    for chem in model.chemicals:
        data.append([chem.formula, "{0:10.4f}".format(chem.mass), "{0:10.4f}".format(chem.mass/model.scale_all), ""])
    data.append(["Sum", "{0:10.4f}".format(sum([c.mass for c in model.chemicals])),
                        "{0:10.4f}".format(sum(c.mass/model.scale_all for x in model.chemicals)), ""])
    tab = Table(data)
    tab.setStyle(res_tab_style)
    return tab

def rescaled_results_table(model):

    masspar = sum([s.mass for s in model.selections])
    masssum = sum([s.mass for s in model.chemicals])

    data = [["Substance", "Mass [g]", "Scaled Mass [g]", "Weighted Mass [g]"]]
    for chem in model.chemicals:
        data.append([chem.formula, "{0:10.4f}".format(chem.mass), "{0:10.4f}".format(chem.mass/model.sample_scale), ""])
    data.append(["Total Sum", "{0:10.4f}".format(masssum),
                        "{0:10.4f}".format(masssum/model.sample_scale), ""])
    tab = Table(data)
    tab.setStyle(res_tab_style)
    return tab

def create_pdf(path, model, flags):

    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=25,leftMargin=25, topMargin=25, bottomMargin=25)

    story = []
    header = create_header(model, flags['title'], flags['author'], flags['email'])
    comps = components_table(model)
    batch = batch_table(model)
    result = results_table(model)
    rescaled_result = rescaled_results_table(model)

    story.extend(header)
    story.append(Spacer(1, 15))
    if flags['composition']:
        story.append(Paragraph("Composition Matrix [C]", styles['Section']))
        story.append(Spacer(1, 15))
        story.append(comps)
        story.append(Spacer(1, 10))
    if flags['batch']:
        story.append(Paragraph("Batch Matrix [B]", styles['Section']))
        story.append(Spacer(1, 15))
        story.append(batch)
        story.append(Spacer(1, 10))
    if flags['rescale_all']:
        story.append(Paragraph("Results [X] (SF={0:8.4f})".format(model.scale_all), styles['Section']))
        story.append(Spacer(1, 15))
        story.append(result)
        story.append(Spacer(1, 10))
    if flags['rescale_to']:
        story.append(Paragraph("Results [X] (SF={0:8.4f})".format(model.sample_scale), styles['Section']))
        story.append(Spacer(1, 15))
        story.append(rescaled_result)
    if flags['comment'] != "":
        story.append(Spacer(1, 10))
        story.append(Paragraph("Comments", styles['Section']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(flags['comment'], styles['Normal']))
    doc.build(story)

def create_pdf_composition(path, model, flags):

    if not model.calculated:
        raise ValueError('Calculation was not performed yet.')
        return

    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=25,leftMargin=25, topMargin=25, bottomMargin=25)

    story = []
    header = create_header(model, flags['title'], flags['author'], flags['email'], no_moles=True)
    chems = chemicals_table(model)
    batch = batch_table(model)
    result = composition_results_table(model)

    story.extend(header)
    story.append(Spacer(1, 20))
    story.append(Paragraph("Chemicals", styles['Section']))
    story.append(Spacer(1, 20))
    story.append(chems)
    story.append(Spacer(1, 10))
    story.append(Paragraph("Batch Matrix [B]", styles['Section']))
    story.append(Spacer(1, 20))
    story.append(batch)
    story.append(Spacer(1, 10))
    if model.item_scale is not None:
        story.append(Paragraph("Results (SF={0:8.4f})".format(model.item_scale), styles['Section']))
    else:
        story.append(Paragraph("Results", styles['Section']))
    story.append(Spacer(1, 20))
    story.append(result)
    if flags['comment'] != "":
        story.append(Spacer(1, 10))
        story.append(Paragraph("Comments", styles['Section']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(flags['comment'], styles['Normal']))

    doc.build(story)
