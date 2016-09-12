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


import datetime
import numpy as np
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

__version__ = "0.2.2"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name='RightJ', alignment=TA_RIGHT))
styles.add(ParagraphStyle(name='LeftJ', alignment=TA_LEFT))
styles.add(ParagraphStyle(name='BlueTitle', alignment=TA_CENTER,
                          textColor=colors.blue, fontSize=22))
styles.add(ParagraphStyle(name='Section', textColor=colors.blue, fontSize=16))
styles.add(ParagraphStyle(name='Compo', alignment=TA_CENTER,
                          textColor=colors.blue, fontSize=14))
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
    ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
    ('LINEBELOW', (0, -2), (-1, -1), 0.5, colors.black),
    ('LINEBEFORE', (-1, 0), (-1, -1), 0.5, colors.black),
    ('LINEBELOW', (-1, 1), (-1, -1), 0.5, colors.black),
])


def volume2str(vol, scale=1.0, fmt="{0:10.4f}"):
    '''Convert volume to string'''

    if vol is not None:
        return fmt.format(vol / scale)
    else:
        return ""


def create_header(model, title, author, synth_id=None, no_moles=False):
    'Creates the header of the report'

    story = []
    if synth_id is not None:
        story.append(Paragraph('Synthesis ID: {0:d}'.format(synth_id),
                               styles['LeftJ']))
    date = datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")
    story.append(Paragraph(date, styles['RightJ']))
    story.append(Paragraph(title, styles['BlueTitle']))
    story.append(Spacer(1, 16))
    if no_moles:
        story.append(Paragraph(ur' : '.join(['{0}'.format(x.html_label()) for x in model.components]), styles['Compo']))
    else:
        story.append(Paragraph(ur' : '.join(['{0}{1}'.format(x.moles, x.html_label()) for x in model.components]), styles['Compo']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(author, styles['CenterJ']))
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
                ['Mol. wt. [g/mol]']+["{0:10.3f}".format(c.molwt) for c in model.components]]
    else:
        data = [['Compound']+[c.formula for c in model.components],
                ['Mole ratio']+["{0:10.3f}".format(c.moles) for c in model.components],
                ['Weight [g]']+["{0:10.3f}".format(c.mass) for c in model.components],
                ['Mol. wt. [g/mol]']+["{0:10.3f}".format(c.molwt) for c in model.components]]

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


def batch_table(session, model):

    temp = np.array(map(lambda x: "{0:8.4f}".format(x), model.get_B_matrix(session).reshape(model.B.size)))
    data = temp.reshape(model.get_B_matrix(session).shape).tolist()
    for row, chemical in zip(data, model.chemicals):
        row.insert(0, chemical.formula + " ({0:6.2f}%)".format(chemical.concentration*100))
    data.insert(0, ['Compound']+[c.formula for c in model.components])
    tab = Table(data)
    tab.setStyle(tab_style)
    return tab


def results_table(model, scale=None):
    '''
    Return a table with the results scaled according to the scale argument
    scale:
        None     : no scaling,
        "all"    : scale all chemicals by a factor,
        "sample" : scale all chemicals to a selected sample size,
        "item"   : scale all chemicals to and item of selected size,
    '''

    if scale is None:
        scale = 1.0
    elif scale == "all":
        scale = model.scale_all
    elif scale == "sample":
        scale = model.sample_scale
    elif scale == "item":
        scale = model.item_scale
    else:
        raise ValueError("wrong scale argument set: {0}".format(scale))

    masssum = sum([s.mass for s in model.chemicals])
    volusum = sum([s.volume for s in model.chemicals if s.volume is not None])

    data = [["Substance", "Formula", "Mass [g]", "Volume [cm3]", "Weighted Mass [g]"]]
    for chem in model.chemicals:
        data.append([chem.listctrl_label(), chem.formula, "{0:10.4f}".format(chem.mass/scale), volume2str(chem.volume, scale=scale), ""])
    data.append(["Sum", "", "{0:10.4f}".format(masssum / scale),
                        "{0:10.4f}".format(volusum / scale), ""])
    tab = Table(data)
    tab.setStyle(res_tab_style)
    return tab


def synthesis_paragraphs(flags):

    story = []

    if 'target' in flags.keys():
        story.append(Paragraph('Target material: {}'.format(flags['target']), styles['Normal']))
        story.append(Spacer(1, 10))
    if 'ref' in flags.keys():
        story.append(Paragraph('Reference: {}'.format(flags['ref']), styles['Normal']))
        story.append(Spacer(1, 10))
    if 'temp' in flags.keys():
        story.append(Paragraph('Temperature [K]: {0}'.format(flags['temp']), styles['Normal']))
        story.append(Spacer(1, 10))
    if 'cryst' in flags.keys():
        story.append(Paragraph('Crystallization time [h]: {0}'.format(flags['cryst']), styles['Normal']))
    if 'desc' in flags.keys():
        story.append(KeepTogether([Spacer(1, 10),
                                   Paragraph("Description", styles['Section']),
                                   Spacer(1, 12),
                                   Paragraph(flags['desc'], styles['Normal'])]))
    return story


def create_pdf(path, session, model, flags):

    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=25, leftMargin=25,
                            topMargin=25, bottomMargin=25)

    story = []
    header = create_header(model, flags['title'], flags['author'], flags['id'])
    comps = components_table(model)
    batch = batch_table(session, model)

    story.extend(header)
    story.append(Spacer(1, 15))

    story.extend(synthesis_paragraphs(flags))
    story.append(Spacer(1, 15))

    if flags['composition']:
        story.append(KeepTogether([Paragraph("Composition Matrix [C]", styles['Section']),
                                   Spacer(1, 15), comps, Spacer(1, 10)]))
    if flags['batch']:
        story.append(KeepTogether([Paragraph("Batch Matrix [B]", styles['Section']),
                                   Spacer(1, 15), batch, Spacer(1, 10)]))
    if flags['rescale_all']:
        story.append(KeepTogether([Paragraph("Results [X] (SF={0:8.4f})".format(model.scale_all), styles['Section']),
                                  Spacer(1, 15), results_table(model, scale="all"), Spacer(1, 10)]))
    if flags['rescale_to']:
        story.append(KeepTogether([Paragraph("Results [X] (SF={0:8.4f})".format(model.sample_scale), styles['Section']),
                                   Spacer(1, 15), results_table(model, scale="sample"), Spacer(1, 10)]))
    if flags['rescale_item']:
        story.append(KeepTogether([Paragraph("Results [X] (SF={0:8.4f})".format(model.item_scale), styles['Section']),
                                   Spacer(1, 15), results_table(model, scale="item"), Spacer(1, 10)]))
    if flags['comment'] != "":
        story.append(KeepTogether([Spacer(1, 10),
                                   Paragraph("Comments", styles['Section']),
                                   Spacer(1, 12),
                                   Paragraph(flags['comment'], styles['Normal'])]))
    doc.build(story)


def create_pdf_composition(path, model, flags):

    if not model.calculated:
        raise ValueError('Calculation was not performed yet.')
        return

    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=25, leftMargin=25,
                            topMargin=25, bottomMargin=25)

    story = []
    header = create_header(model, flags['title'], flags['author'], no_moles=True)
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
