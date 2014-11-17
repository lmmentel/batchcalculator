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

import os
import sys

from ObjectListView import ObjectListView, ColumnDefn

import wx
import wx.lib.agw.genericmessagedialog as GMD

def which(prog):
    '''
    Python equivalent of the unix which command, returns the absolute path of
    the "prog" if it is found on the system PATH.
    '''

    if sys.platform == "win32":
        prog += ".exe"
    for path in os.getenv('PATH').split(os.path.pathsep):
        fprog = os.path.join(path, prog)
        if os.path.exists(fprog) and os.access(fprog, os.X_OK):
            return fprog

class AddBatchToDatabaseDialog(wx.Dialog):

    def __init__(self, parent, model, id=wx.ID_ANY, title="Add a Batch record to the Database",
            pos=wx.DefaultPosition, size=(400, 400),
            style=wx.DEFAULT_FRAME_STYLE, name="add chemical"):

        super(AddBatchToDatabaseDialog, self).__init__(parent, id, title, pos, size, style, name)

        panel = wx.Panel(self)

        # attributes

        lbl_chemical = wx.StaticText(panel, -1, "Chemical")
        lbl_component = wx.StaticText(panel, -1, "Component")
        lbl_coeff = wx.StaticText(panel, -1, "Coefficient")
        lbl_reaction = wx.StaticText(panel, -1, "Reaction")

        txtc_coeff = wx.TextCtrl(panel, -1, "")

        chemicals = model.get_chemicals(showall=True)
        components = model.get_components()
        reactions = model.get_reactions()

        self.ch_chemical  = wx.Choice(panel, -1, (100, 50), choices=[x.name for x in chemicals])
        self.ch_component = wx.Choice(panel, -1, (100, 50), choices=[x.name for x in components])
        self.ch_reaction  = wx.Choice(panel, -1, (100, 50), choices=[x.reaction for x in reactions])

        sizer = wx.GridBagSizer(vgap=5, hgap=5)
        sizer.Add(lbl_chemical,  pos=(0, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_component, pos=(1, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_coeff,     pos=(2, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_reaction,  pos=(3, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)

        sizer.Add(self.ch_chemical,  pos=(0, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.ch_component, pos=(1, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(txtc_coeff,        pos=(2, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.ch_reaction,  pos=(3, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)

        sizer.AddGrowableCol(1)
        panel.SetSizerAndFit(sizer)

class AddModifyChemicalDialog(wx.Dialog):

    def __init__(self, parent, model, id=wx.ID_ANY, title="Add a Chemical to the Database",
            pos=wx.DefaultPosition, size=(400, 400),
            style=wx.DEFAULT_FRAME_STYLE, name="add chemical"):

        super(AddModifyChemicalDialog, self).__init__(parent, id, title, pos, size, style, name)

        panel = wx.Panel(self)

        # attributes

        lbl_name = wx.StaticText(panel, -1, "Name")
        lbl_formula = wx.StaticText(panel, -1, "Formula")
        lbl_molwt = wx.StaticText(panel, -1, "Molecular Weight")
        lbl_shname = wx.StaticText(panel, -1, "Short Name")
        lbl_conc = wx.StaticText(panel, -1, "Concentration")
        lbl_cas = wx.StaticText(panel, -1, "CAS")
        lbl_density = wx.StaticText(panel, -1, "Density")
        lbl_pk = wx.StaticText(panel, -1, "pK")
        lbl_smiles = wx.StaticText(panel, -1, "SMILES")
        lbl_type = wx.StaticText(panel, -1, "Type")
        lbl_form = wx.StaticText(panel, -1, "Physical Form")
        lbl_elect = wx.StaticText(panel, -1, "Electrolyte")

        self.txtc_name = wx.TextCtrl(panel, -1, "")
        self.txtc_formula = wx.TextCtrl(panel, -1, "")
        self.txtc_molwt = wx.TextCtrl(panel, -1, "")
        self.txtc_shname = wx.TextCtrl(panel, -1, "")
        self.txtc_conc = wx.TextCtrl(panel, -1, "")
        self.txtc_cas = wx.TextCtrl(panel, -1, "")
        self.txtc_density = wx.TextCtrl(panel, -1, "")
        self.txtc_pk = wx.TextCtrl(panel, -1, "")
        self.txtc_smiles = wx.TextCtrl(panel, -1, "")

        types = model.get_types()
        forms = model.get_physical_forms()
        elects = model.get_electrolytes()

        self.ch_type = wx.Choice(panel, -1, (100, 50), choices=[x.name for x in types])
        self.ch_form = wx.Choice(panel, -1, (100, 50), choices=[x.form for x in forms])
        self.ch_elects = wx.Choice(panel, -1, (100, 50), choices=[x.name for x in elects])

        sizer = wx.GridBagSizer(vgap=5, hgap=5)
        sizer.Add(lbl_name,    pos=( 0, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_formula, pos=( 1, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_molwt,   pos=( 2, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_shname,  pos=( 3, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_conc,    pos=( 4, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_cas,     pos=( 5, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_density, pos=( 6, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_pk,      pos=( 7, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_smiles,  pos=( 8, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_type,    pos=( 9, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_form,    pos=(10, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_elect,   pos=(11, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)

        sizer.Add(self.txtc_name,    pos=( 0, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.txtc_formula, pos=( 1, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.txtc_molwt,   pos=( 2, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.txtc_shname,  pos=( 3, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.txtc_conc,    pos=( 4, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.txtc_cas,     pos=( 5, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.txtc_density, pos=( 6, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.txtc_pk,      pos=( 7, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.txtc_smiles,  pos=( 8, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.ch_type,      pos=( 9, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.ch_form,      pos=(10, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.ch_elects,    pos=(11, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)

        sizer.AddGrowableCol(1)
        panel.SetSizerAndFit(sizer)

    def get_data(self):

        chem_dict = {
            "name"       : self.txtc_name.GetValue(),
            "formula"    : self.txtc_formula.GetValue(),
            "molwt"      : self.txtc_molwt.GetValue(),
            "short_name" : self.txtc_shname.GetValue(),
            "concentration" : self.txtc_conc.GetValue(),
            "cas" : self.txtc_cas.GetValue(),
            "density" : self.txtc_density.GetValue(),
            "pk" : self.txtc_pk.GetValue(),
            "smiles" : self.txtc_smiles.GetValue(),
        }

        return chem_dict

class AddComponentToDatabaseDialog(wx.Dialog):

    def __init__(self, parent, model, id=wx.ID_ANY, title="Add a Component to the Database",
            pos=wx.DefaultPosition, size=(400, 400),
            style=wx.DEFAULT_FRAME_STYLE, name="add chemical"):

        super(AddComponentToDatabaseDialog, self).__init__(parent, id, title, pos, size, style, name)

        panel = wx.Panel(self)

        # attributes

        lbl_name = wx.StaticText(panel, -1, "Name")
        lbl_formula = wx.StaticText(panel, -1, "Formula")
        lbl_molwt = wx.StaticText(panel, -1, "Molecular Weight")
        lbl_shname = wx.StaticText(panel, -1, "Short Name")
        lbl_category = wx.StaticText(panel, -1, "Category")

        txtc_name = wx.TextCtrl(panel, -1, "")
        txtc_formula = wx.TextCtrl(panel, -1, "")
        txtc_molwt = wx.TextCtrl(panel, -1, "")
        txtc_shname = wx.TextCtrl(panel, -1, "")

        categs = model.get_categories()

        self.ch_category = wx.Choice(panel, -1, (100, 50), choices=[x.name for x in categs])

        sizer = wx.GridBagSizer(vgap=5, hgap=5)
        sizer.Add(lbl_name,     pos=(0, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_formula,  pos=(1, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_molwt,    pos=(2, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_shname,   pos=(3, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(lbl_category, pos=(4, 0), span=(1, 1), flag=wx.LEFT|wx.RIGHT, border=10)

        sizer.Add(txtc_name,        pos=(0, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(txtc_formula,     pos=(1, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(txtc_molwt,       pos=(2, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(txtc_shname,      pos=(3, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)
        sizer.Add(self.ch_category, pos=(4, 1), span=(1, 1), flag=wx.LEFT|wx.EXPAND|wx.RIGHT, border=10)

        sizer.AddGrowableCol(1)
        panel.SetSizerAndFit(sizer)

class ComponentDialog(wx.Dialog):

    def __init__(self, parent, model, columns, id=wx.ID_ANY, title="",
            pos=wx.DefaultPosition, size=(730, 500),
            style=wx.DEFAULT_FRAME_STYLE, name="Component Dialog"):

        dlgwidth = sum([c["width"] for c in columns]) + 50
        super(ComponentDialog, self).__init__(parent, id, title, pos, (dlgwidth, 500), style, name)

        panel = wx.Panel(self)

        self.compsOlv = ObjectListView(panel, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER,
                useAlternateBackColors=True)
        self.compsOlv.evenRowsBackColor="#DCF0C7"
        self.compsOlv.oddRowsBackColor="#FFFFFF"
        self.compsOlv.CellEditMode = ObjectListView.CELLEDIT_SINGLECLICK

        self.SetComponents(model, columns)

        sizer = wx.FlexGridSizer(rows=2, cols=1, hgap=10, vgap=10)

        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(0)
        sizer.Add(self.compsOlv, flag=wx.GROW | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=5)

        buttonok = wx.Button(panel, id=wx.ID_OK)
        buttonok.SetDefault()
        buttoncancel = wx.Button(panel, id=wx.ID_CANCEL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(buttoncancel, flag=wx.RIGHT, border=10)
        hbox.Add(buttonok)
        sizer.Add(hbox, flag=wx.ALIGN_RIGHT|wx.BOTTOM|wx.RIGHT, border=10)

        panel.SetSizer(sizer)
        panel.Fit()

    def SetComponents(self, model, columns):

        olv_cols = []
        for col in columns:
            olv_cols.append(ColumnDefn(**col))

        self.compsOlv.SetColumns(olv_cols)
        self.compsOlv.CreateCheckStateColumn()
        data = model.get_components()
        for item in data:
            if item.id in [r.id for r in model.components]:
                self.compsOlv.SetCheckState(item, True)
                comp = model.select_item("components", "id", item.id)
                item.moles = comp.moles
        self.compsOlv.SetObjects(data)

    def GetCurrentSelections(self):
        return self.compsOlv.GetCheckedObjects()

class Exceptiondialog(GMD.GenericMessageDialog):
    def __init__(self, msg):
        '''constructor'''
        GMD.GenericMessageDialog.__init__(self, None, msg, "Exception!",
                                              wx.OK|wx.ICON_ERROR)

class ExportTexDialog(wx.Dialog):
    '''
    A dialog for setting the options of the tex report.
    '''

    def __init__(self, parent, id=wx.ID_ANY, title="",
            pos=wx.DefaultPosition, size=(400, 550),
            style=wx.DEFAULT_FRAME_STYLE, name="Export Tex Dialog"):

        super(ExportTexDialog, self).__init__(parent, id, title, pos, size,
                                              style, name)

        panel = wx.Panel(self)

        top_lbl = wx.StaticText(panel, -1, "TeX document options")
        top_lbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        title_lbl = wx.StaticText(panel, -1, "Title:")
        title = wx.TextCtrl(panel, -1, "")
        author_lbl = wx.StaticText(panel, -1, "Author:")
        author = wx.TextCtrl(panel, -1, "")
        email_lbl = wx.StaticText(panel, -1, "Email:")
        email = wx.TextCtrl(panel, -1, "")

        export_btn = wx.Button(panel, id=wx.ID_OK, label="Export")
        cancel_btn = wx.Button(panel, id=wx.ID_CANCEL)

        cb_cmpm = wx.CheckBox(panel, label="Composition Matrix")
        cb_bmat = wx.CheckBox(panel, label="Batch Matrix")
        cb_rescaleall = wx.CheckBox(panel, label="Result vector X (rescaled by a factor)")
        cb_rescaleto = wx.CheckBox(panel, label="Result vector X (rescaled to the sample size)")

        cb_cmpm.SetValue(True)
        cb_bmat.SetValue(True)
        cb_rescaleAll.SetValue(True)
        cb_rescaleTo.SetValue(True)

        cb_calo = wx.CheckBox(panel, label="Calcination I")
        cb_ione = wx.CheckBox(panel, label="Ion Exchange")
        cb_calt = wx.CheckBox(panel, label="Calcination II")

        cb_xrd = wx.CheckBox(panel, label="XRD")
        cb_sem = wx.CheckBox(panel, label="SEM")

        cb_pdf = wx.CheckBox(panel, label="Typeset PDF")
        pdflatex_path = which("pdflatex")
        if pdflatex_path is None:
            pdflatex_path = ""
        self.pdflatex = wx.TextCtrl(panel, -1, pdflatex_path)
        self.pdflatex.Enable(False)

        sb_calculation = wx.StaticBox(panel, label="Include")
        sbc_bs = wx.StaticBoxSizer(sb_calculation, wx.VERTICAL)
        sbc_bs.Add(cb_cmpm, flag=wx.LEFT|wx.TOP, border=5)
        sbc_bs.Add(cb_bmat, flag=wx.LEFT|wx.TOP, border=5)
        sbc_bs.Add(cb_rescaleAll, flag=wx.LEFT|wx.TOP, border=5)
        sbc_bs.Add(cb_rescaleTo, flag=wx.LEFT|wx.TOP, border=5)

        sb_synthesis = wx.StaticBox(panel, label="Synthesis")
        sbs_bs = wx.StaticBoxSizer(sb_synthesis, wx.VERTICAL)
        sbs_bs.Add(cb_calo, flag=wx.LEFT|wx.TOP, border=5)
        sbs_bs.Add(cb_ione, flag=wx.LEFT|wx.TOP, border=5)
        sbs_bs.Add(cb_calt, flag=wx.LEFT|wx.TOP, border=5)

        sb_analysis = wx.StaticBox(panel, label="Analysis")
        sba_bs = wx.StaticBoxSizer(sb_analysis, wx.VERTICAL)
        sba_bs.Add(cb_xrd, flag=wx.LEFT|wx.TOP, border=5)
        sba_bs.Add(cb_sem, flag=wx.LEFT|wx.TOP, border=5)

        self.widgets = {
            "title" : title,
            "author" : author,
            "email" : email,
            "composition" : cb_cmpm,
            "batch" : cb_bmat,
            "rescale_all" : cb_rescaleAll,
            "rescale_to" : cb_rescaleTo,
            "calcination_i" : cb_calo,
            "ion_exchange" : cb_ione,
            "calcination_ii" : cb_calt,
            "xrd" : cb_xrd,
            "sem" : cb_sem,
            "typeset" : cb_pdf,
            "pdflatex" : self.pdflatex,
        }

        # layout

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(top_lbl, 0, wx.ALL, 5)
        main_sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        fgs_title = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        fgs_title.AddGrowableCol(1)
        fgs_title.Add(title_lbl, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(title, 0, wx.EXPAND)
        fgs_title.Add(author_lbl, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(author, 0, wx.EXPAND)
        fgs_title.Add(email_lbl, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(email, 0, wx.EXPAND)

        main_sizer.Add(fgs_title, 0, wx.EXPAND|wx.ALL, 10)
        main_sizer.Add(sbc_bs, 0, wx.EXPAND|wx.ALL, 10)

        gbs = wx.GridBagSizer(hgap=5, vgap=5)
        gbs.Add(sbs_bs, pos=(0, 0), flag=wx.ALIGN_RIGHT|wx.GROW|wx.ALL, border=10)
        gbs.Add(sba_bs, pos=(0, 1), flag=wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border=10)
        gbs.AddGrowableCol(0)
        gbs.AddGrowableCol(1)

        main_sizer.Add(gbs, 0, wx.EXPAND|wx.ALL, border=10)

        fgs0 = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        fgs0.AddGrowableCol(1)
        fgs0.Add(cb_pdf, flag=wx.ALIGN_LEFT|wx.LEFT|wx.BOTTOM, border=10)
        fgs0.Add(self.pdflatex, flag=wx.EXPAND|wx.LEFT|wx.BOTTOM|wx.RIGHT, border=10)
        main_sizer.Add(fgs0, flag=wx.EXPAND|wx.ALL, border=5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(cancel_btn, 0, wx.LEFT|wx.RIGHT, 10)
        hbox.Add(export_btn, 0, wx.LEFT|wx.RIGHT, 10)

        main_sizer.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.RIGHT, 10)
        panel.SetSizerAndFit(main_sizer)

        # events

        cb_pdf.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)

    def EvtCheckBox(self, event):
        cb = event.GetEventObject()
        if cb.isChecked():
            self.pdflatex.Enable(True)

    def getdata(self):

        res = dict()
        for name, attr in self.widgets.items():
            res[name] = attr.GetValue()
        return res

class ReactantDialog(wx.Dialog):

    def __init__(self, parent, model, columns, id=wx.ID_ANY, title="",
            pos=wx.DefaultPosition, size=(850, 520),
            style=wx.DEFAULT_FRAME_STYLE, name="Reactant Dialog"):

        dlgwidth = sum([c["width"] for c in columns]) + 60
        super(ReactantDialog, self).__init__(parent, id, title, pos, (dlgwidth, 500), style, name)

        panel = wx.Panel(self)

        self.reacsOlv = ObjectListView(panel, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER,
                useAlternateBackColors=True)
        self.reacsOlv.evenRowsBackColor="#DCF0C7"
        self.reacsOlv.oddRowsBackColor="#FFFFFF"
        self.reacsOlv.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK

        self.SetReactants(model, columns)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.reacsOlv, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        buttonOk = wx.Button(panel, id=wx.ID_OK)
        buttonOk.SetDefault()
        buttonCancel = wx.Button(panel, id=wx.ID_CANCEL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(buttonCancel, flag=wx.RIGHT, border=10)
        hbox.Add(buttonOk)
        self.sizer.Add(hbox, flag=wx.ALIGN_RIGHT|wx.ALL, border=10)

        panel.SetSizerAndFit(self.sizer)

    def SetReactants(self, model, columns):

        olv_cols = []
        for col in columns:
            olv_cols.append(ColumnDefn(**col))

        self.reacsOlv.SetColumns(olv_cols)
        self.reacsOlv.CreateCheckStateColumn()
        data = model.get_chemicals(showall=(len(model.components) == 0))
        for item in data:
            if item.id in [r.id for r in model.reactants]:
                self.reacsOlv.SetCheckState(item, True)
                reac = model.select_item("reactants", "id", item.id)
                item.mass = reac.mass
                item.concentration = reac.concentration
        self.reacsOlv.SetObjects(data)

    def GetCurrentSelections(self):
        return self.reacsOlv.GetCheckedObjects()

class RescaleToItemDialog(wx.Dialog):

    def __init__(self, parent, model, columns, id=wx.ID_ANY, title="Choose an item and the amount",
            pos=wx.DefaultPosition, size=(400, 400),
            style=wx.DEFAULT_FRAME_STYLE, name="Rescale to Item Dialog"):
        super(RescaleToItemDialog, self).__init__(parent, id, title, pos, size, style, name)

        panel = wx.Panel(self)

        self.olv = ObjectListView(panel, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER,
                useAlternateBackColors=True)
        self.olv.evenRowsBackColor="#DCF0C7"
        self.olv.oddRowsBackColor="#FFFFFF"
        self.SetComponents(model, columns)
        scalelbl = wx.StaticText(panel, -1, "Amount:")
        self.amount = wx.TextCtrl(panel, -1, "{0:6.2f}".format(1.0))

        buttonOk = wx.Button(panel, id=wx.ID_OK)
        buttonOk.SetDefault()
        buttonCancel = wx.Button(panel, id=wx.ID_CANCEL)

        # layout

        sizer = wx.GridBagSizer(vgap=5, hgap=5)
        sizer.Add(self.olv, pos=(0, 0), span=(1, 4), flag=wx.GROW|wx.ALL, border=5)
        sizer.Add(scalelbl,  pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        sizer.Add(self.amount, pos=(1, 1), span=(1, 2), flag=wx.EXPAND|wx.ALIGN_LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        sizer.Add(buttonCancel, pos=(2, 2), flag=wx.BOTTOM, border=10)
        sizer.Add(buttonOk, pos=(2, 3), flag=wx.BOTTOM|wx.RIGHT, border=10)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(0)
        panel.SetSizer(sizer)

    def SetComponents(self, model, columns):

        olv_cols = []
        for col in columns:
            olv_cols.append(ColumnDefn(**col))

        self.olv.SetColumns(olv_cols)
        self.olv.CreateCheckStateColumn()
        self.olv.SetObjects(model.components)

    def GetCurrentSelections(self):
        return self.amount.GetValue(), self.olv.GetCheckedObjects()

class RescaleToSampleDialog(wx.Dialog):

    def __init__(self, parent, model, columns, id=wx.ID_ANY, title="Choose compounds and sample size ...",
                 pos=wx.DefaultPosition, size=(400, 400),
                 style=wx.DEFAULT_FRAME_STYLE, name="Rescale to Sample Dialog"):

        super(RescaleToSampleDialog, self).__init__(parent, id, title, pos, size, style, name)

        panel = wx.Panel(self)

        self.olv = ObjectListView(panel, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER,
                useAlternateBackColors=True)
        self.olv.evenRowsBackColor="#DCF0C7"
        self.olv.oddRowsBackColor="#FFFFFF"
        self.SetReactants(model, columns)

        scalelbl = wx.StaticText(panel, -1, "Sample size [g]:")
        self.sample_size = wx.TextCtrl(panel, -1, str(model.sample_size))

        buttonOk = wx.Button(panel, id=wx.ID_OK)
        buttonOk.SetDefault()
        buttonCancel = wx.Button(panel, id=wx.ID_CANCEL)

        # layout

        sizer = wx.GridBagSizer(vgap=5, hgap=5)
        sizer.Add(self.olv, pos=(0, 0), span=(1, 4), flag=wx.GROW|wx.ALL, border=5)
        sizer.Add(scalelbl,  pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        sizer.Add(self.sample_size, pos=(1, 1), span=(1, 2), flag=wx.EXPAND|wx.ALIGN_LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        sizer.Add(buttonCancel, pos=(2, 2), flag=wx.BOTTOM, border=10)
        sizer.Add(buttonOk, pos=(2, 3), flag=wx.BOTTOM|wx.RIGHT, border=10)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(0)
        panel.SetSizer(sizer)

    def SetReactants(self, model, columns):

        olv_cols = []
        for col in columns:
            olv_cols.append(ColumnDefn(**col))

        self.olv.SetColumns(olv_cols)
        self.olv.CreateCheckStateColumn()
        for item in model.reactants:
            self.olv.Check(item)
        self.olv.SetObjects(model.reactants)

    def GetCurrentSelections(self):
        return self.sample_size.GetValue(), self.olv.GetCheckedObjects()
