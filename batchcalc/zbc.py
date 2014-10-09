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

__version__ = "0.1.0"

import os
import pickle
import re
import subprocess
import sys
import traceback
from collections import namedtuple, OrderedDict

from numpy.linalg import inv
import numpy as np

import wx
import wx.grid as gridlib
import wx.lib.mixins.listctrl as listmix
from wx.lib.wordwrap import wordwrap
import wx.lib.agw.genericmessagedialog as GMD
# ObjectListView
from ObjectListView import ObjectListView, ColumnDefn
# uncomment for debugging
#import wx.lib.inspection

from batchcalc.tex_writer import get_report_as_string
from batchcalc.calculator import BatchCalculator, Component

column = namedtuple("column", ["name", "format", "width", "align", "isEditable"])

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

def clean_tex(fname):
    '''
    Clean the auxiliary tex files.
    '''
    exts = [".out", ".aux", ".log", ".tex"]
    fbase = os.path.splitext(fname)[0]
    for fil in [fbase + ext for ext in exts]:
        if os.path.exists(fil):
            os.remove(fil)

class CheckableListCtrl(wx.ListCtrl, listmix.CheckListCtrlMixin, listmix.ListCtrlAutoWidthMixin):

    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.CheckListCtrlMixin.__init__(self)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        self.current_selections = list()

    def OnCheckItem(self, index, flag):
        self.current_selections[index] = not self.current_selections[index]

class ResizableListCtrl(wx.ListCtrl, listmix.CheckListCtrlMixin, listmix.ListCtrlAutoWidthMixin):

    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

class ShowBFrame(wx.Frame):
    def __init__(self, parent, log, id=wx.ID_ANY, title="Batch Matrix",
            pos=wx.DefaultPosition, size=(500, 300),
            style=wx.DEFAULT_FRAME_STYLE, name="Show Batch Matrix Dialog"):

        super(ShowBFrame, self).__init__(parent, id, title, pos, size, style, name)

        panel = wx.Panel(self, -1, style=0)
        grid = CustTableGrid(panel, parent.model)
        okbtn = wx.Button(panel, wx.ID_OK)
        okbtn.Bind(wx.EVT_BUTTON, self.OnOKButton)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.GROW|wx.ALL, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(okbtn)
        sizer.Add(hbox, flag=wx.ALIGN_RIGHT|wx.ALL, border=10)
        panel.SetSizer(sizer)

    def OnOKButton(self, evt):
        self.Close()

    def OnButtonFocus(self, evt):
        print "button focus"

class CustomDataTable(gridlib.PyGridTableBase):
    def __init__(self, model):
        gridlib.PyGridTableBase.__init__(self)

        self.col_labels = [x.listctrl_label() for x in model.components]
        self.row_labels = [x.listctrl_label() for x in model.reactants]

        self.data_types = [gridlib.GRID_VALUE_FLOAT]*len(model.reactants)

        self.data = model.B.tolist()

    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        def innerSetValue(row, col, value):
            try:
                self.data[row][col] = value
            except IndexError:
                # add a new row
                self.data.append([''] * self.GetNumberCols())
                innerSetValue(row, col, value)

                # tell the grid we've added a row
                msg = gridlib.GridTableMessage(self,            # The table
                        gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                        1                                       # how many
                        )

                self.GetView().ProcessTableMessage(msg)
        innerSetValue(row, col, value)

    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.col_labels[col]

    # Called when the grid needs to display row labels
    def GetRowLabelValue(self, row):
        return self.row_labels[row]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.data_types[col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        colType = self.data_types[col].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)

class CustTableGrid(gridlib.Grid):
    def __init__(self, parent, model):
        gridlib.Grid.__init__(self, parent, -1)

        table = CustomDataTable(model)

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)

        #self.SetRowLabelSize(0)
        self.SetMargins(5,5)
        self.AutoSizeColumns(True)
        for i in range(self.GetNumberRows()):
            self.SetColFormatFloat(i, width=10, precision=4)
        self.SetRowLabelSize(100)

        gridlib.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)


    # I do this because I don't like the default behaviour of not starting the
    # cell editor on double clicks, but only a second click.
    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

class RescaleToDialog(wx.Dialog):

    def __init__(self, parent, model, id=wx.ID_ANY, title="Choose compounds and sample size ...",
            pos=wx.DefaultPosition, size=(470, 400),
            style=wx.DEFAULT_FRAME_STYLE, name="Rescale to Dialog"):

        super(RescaleToDialog, self).__init__(parent, id, title, pos, size, style, name)

        panel = wx.Panel(self)

        self.clist = CheckableListCtrl(panel, style=wx.LC_SINGLE_SEL|wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.clist.InsertColumn(0, "Name", format=wx.LIST_FORMAT_LEFT, width=200)
        self.clist.InsertColumn(1, "Formula", format=wx.LIST_FORMAT_LEFT, width=150)
        self.clist.InsertColumn(2, "Mass [g]", format=wx.LIST_FORMAT_RIGHT, width=100)

        for i, reac in enumerate(model.reactants):
            self.clist.current_selections.append(False)
            self.clist.Append([reac.name, reac.listctrl_label(), "{0:10.4f}".format(reac.mass)])
            self.clist.CheckItem(i, True)
            if i not in model.selections:
                self.clist.CheckItem(i, False)

        scalelbl = wx.StaticText(panel, -1, "Sample size [g]:")
        self.sample_size = wx.TextCtrl(panel, -1, str(model.sample_size))

        buttonOK = wx.Button(panel, id=wx.ID_OK)
        buttonOK.SetDefault()
        buttonCancel = wx.Button(panel, id=wx.ID_CANCEL)

        # Layout

        sizer = wx.GridBagSizer(vgap=5, hgap=5)
        sizer.Add(self.clist, pos=(0, 0), span=(1, 4), flag=wx.GROW|wx.ALL, border=5)

        sizer.Add(scalelbl,  pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        sizer.Add(self.sample_size, pos=(1, 1), span=(1, 2), flag=wx.EXPAND|wx.ALIGN_LEFT|wx.RIGHT|wx.BOTTOM, border=10)

        sizer.Add(buttonCancel, pos=(2, 2), flag=wx.BOTTOM, border=10)
        sizer.Add(buttonOK, pos=(2, 3), flag=wx.BOTTOM|wx.RIGHT, border=10)

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(0)

        panel.SetSizer(sizer)

    def GetCurrentSelections(self):
        cs = self.clist.current_selections
        selected_rows = [x for x in range(len(cs)) if cs[x]]
        sample_size = self.sample_size.GetValue()
        return sample_size, selected_rows

class ComponentDialog(wx.Dialog):

    def __init__(self, parent, model, component, id=wx.ID_ANY, title="Default window title",
            pos=wx.DefaultPosition, size=(590, 300),
            style=wx.DEFAULT_FRAME_STYLE, name="Component Dialog"):

        cols = ["id", "name", "formula", "moles", "molwt", "short"]
        dlgwidth = sum([parent.main.columns[key].width for key in cols]) + 15
        super(ComponentDialog, self).__init__(parent, id, title, pos, (dlgwidth, 620), style, name)

        panel = wx.Panel(self)

        self.compsOlv = ObjectListView(panel, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.compsOlv.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK

        self.SetComponents(model)

        sizer = wx.FlexGridSizer(rows=2, cols=1, hgap=10, vgap=10)

        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(0)
        sizer.Add(self.compsOlv, flag=wx.GROW | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=5)

        buttonOK = wx.Button(panel, id=wx.ID_OK)
        buttonOK.SetDefault()
        buttonCancel = wx.Button(panel, id=wx.ID_CANCEL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(buttonCancel, flag=wx.RIGHT, border=10)
        hbox.Add(buttonOK)
        sizer.Add(hbox, flag=wx.ALIGN_RIGHT|wx.ALL, border=10)

        panel.SetSizer(sizer)
        panel.Fit()

    def SetComponents(self, model, data=None):

        self.compsOlv.SetColumns([
            ColumnDefn("Name", "left", 150, "name", isEditable=False),
            ColumnDefn("Formula", "left", 100, "formula", isEditable=False),
            ColumnDefn("Moles", "right", 100, "moles", isEditable=True, stringConverter="%.2f"),
            ColumnDefn("Category", "left", 100, "category", isEditable=False),
            ColumnDefn("Molecular Wight", "right", 120, "molwt", isEditable=False, stringConverter="%.3f"),
            ColumnDefn("Short Name", "left", 120, "short_name", isEditable=False),
        ])
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

class ReactantDialog(wx.Dialog):

    def __init__(self, parent, model, id=wx.ID_ANY, title="Choose Reactants",
            pos=wx.DefaultPosition, size=(820, 320),
            style=wx.DEFAULT_FRAME_STYLE, name="Reactant Dialog"):

        cols = ["id", "name", "formula", "conc", "molwt", "short", "typ", "cas"]
        dlgwidth = sum([parent.main.columns[key].width for key in cols]) + 15
        super(ReactantDialog, self).__init__(parent, id, title, pos, (dlgwidth, 620), style, name)

        panel = wx.Panel(self)

        self.reacsOlv = ObjectListView(panel, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.reacsOlv.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK

        self.SetReactants(model)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.reacsOlv, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        buttonOK = wx.Button(panel, id=wx.ID_OK)
        buttonOK.SetDefault()
        buttonCancel = wx.Button(panel, id=wx.ID_CANCEL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(buttonCancel, flag=wx.RIGHT, border=10)
        hbox.Add(buttonOK)
        self.sizer.Add(hbox, flag=wx.ALIGN_RIGHT|wx.ALL, border=10)

        panel.SetSizerAndFit(self.sizer)

    def SetReactants(self, model, data=None):

        self.reacsOlv.SetColumns([
            ColumnDefn("Name", "left", 150, "name", isEditable=False),
            ColumnDefn("Formula", "left", 100, "formula", isEditable=False),
            ColumnDefn("Concentration", "right", 100, "concentration", isEditable=True, stringConverter="%.2f"),
            ColumnDefn("Molecular Wight", "right", 120, "molwt", isEditable=False, stringConverter="%.3f"),
            ColumnDefn("Short Name", "left", 120, "short_name", isEditable=False),
            ColumnDefn("Type", "left", 120, "typ", isEditable=False),
            ColumnDefn("CAS No.", "left", 120, "cas", isEditable=False),
        ])
        self.reacsOlv.CreateCheckStateColumn()
        data = model.get_chemicals(showall=(len(model.components) == 0))
        for item in data:
            if item.id in [r.id for r in model.reactants]:
                self.reacsOlv.SetCheckState(item, True)
        self.reacsOlv.SetObjects(data)

    def GetCurrentSelections(self):
        return self.reacsOlv.GetCheckedObjects()

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
        cb_rescaleAll = wx.CheckBox(panel, label="Result vector X (rescaled by a factor)")
        cb_rescaleTo = wx.CheckBox(panel, label="Result vector X (rescaled to the sample size)")

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

        # Layout

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

        # Events

        cb_pdf.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)

    def EvtCheckBox(self, event):
        cb = event.GetEventObject()
        if cb.IsChecked():
            self.pdflatex.Enable(True)

    def GetData(self):

        res = dict()
        for name, attr in self.widgets.items():
            res[name] = attr.GetValue()
        return res

def compRowFormatter(listItem, Component):
    red    = "#FF6B66"
    yellow = "#FFDE66"
    orange = "#FF9166"
    green  = "#D4FF66"
    gray   = "#939393"

    if Component.category == "zeolite":
        listItem.SetBackgroundColour(red)
    elif Component.category == "template":
        listItem.SetBackgroundColour(yellow)
    elif Component.category == "zgm":
        listItem.SetBackgroundColour(orange)

class InputPanel(wx.Panel):

    def __init__(self, parent, main):
        super(InputPanel, self).__init__(parent, style=wx.SUNKEN_BORDER)

        # Attributes

        self.main = main

        cmptxt = wx.StaticText(self, -1, label="Components")
        rcttxt = wx.StaticText(self, -1, label="Reactants")

        self.compOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.compOlv.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK
        self.compOlv.rowFormatter = compRowFormatter

        self.reacOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.reacOlv.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK

        self.SetComponents()
        self.SetReactants()
        zeobtn = wx.Button(self, -1, label="Edit")
        rctbtn = wx.Button(self, -1, label="Edit")

        # Layout

        fgs = wx.FlexGridSizer(rows=3, cols=2, hgap=10, vgap=10)

        fgs.AddGrowableCol(0)
        fgs.AddGrowableCol(1)
        fgs.AddGrowableRow(1)

        fgs.Add(cmptxt, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border=5)
        fgs.Add(rcttxt, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border=5)

        fgs.Add(self.compOlv, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.GROW|wx.LEFT, border=10)
        fgs.Add(self.reacOlv, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.GROW|wx.RIGHT, border=10)

        fgs.Add(zeobtn, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, border=5)
        fgs.Add(rctbtn, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, border=5)
        self.SetSizer(fgs)
        self.Fit()

        # Event Handlers

        zeobtn.Bind(wx.EVT_BUTTON, self.OnEditZeolites)
        rctbtn.Bind(wx.EVT_BUTTON, self.OnEditReactants)

    def SetComponents(self, data=None):

        self.compOlv.SetColumns([
            ColumnDefn("Label", "left", 100, "listctrl_label", isEditable=False, isSpaceFilling=True),
            ColumnDefn("Moles", "right", 100, "moles", isEditable=True, stringConverter="%.2f"),
        ])
        self.compOlv.SetObjects(self.main.model.components)

    def SetReactants(self, data=None):

        self.reacOlv.SetColumns([
            ColumnDefn("Label", "left", 100, "listctrl_label", isEditable=False, isSpaceFilling=True),
            ColumnDefn("Concentration", "right", 100, "concentration", isEditable=True, stringConverter="%.2f"),
        ])
        self.reacOlv.SetObjects(self.main.model.reactants)

    def OnEditZeolites(self, event):
        '''
        Show the dialog with the zeolite components retrieved from the
        database.
        '''

        self.dlg = ComponentDialog(self, self.main.model, "zeolite", id=-1, title="Choose Zeolite Components...")
        result = self.dlg.ShowModal()
        if result == wx.ID_OK:
            self.main.model.components = self.dlg.GetCurrentSelections()
        self.compOlv.SetObjects(self.main.model.components)
        self.dlg.Destroy()

    def OnEditReactants(self, event):
        '''
        Show the dialog with the reactants retrieved from the database.
        '''

        self.dlg = ReactantDialog(self, self.main.model, id=-1)
        result = self.dlg.ShowModal()
        if result == wx.ID_OK:
            self.main.model.reactants = self.dlg.GetCurrentSelections()
        self.reacOlv.SetObjects(self.main.model.reactants)
        self.dlg.Destroy()

class OutputPanel(wx.Panel):

    def __init__(self, parent, main):
        super(OutputPanel, self).__init__(parent, style=wx.SUNKEN_BORDER)

        # Attributes

        resulttxt = wx.StaticText(self, -1, label="Results [X]")
        self.rescalealltxt = wx.StaticText(self, -1, label="Rescaled by")
        self.rescaletotxt = wx.StaticText(self, -1, label="Rescaled to")

        self.resultlst = ResizableListCtrl(self, style=wx.LC_REPORT, size=(200, -1))
        self.rescalealllst = ResizableListCtrl(self, style=wx.LC_REPORT, size=(200, -1))
        self.rescaletolst = ResizableListCtrl(self, style=wx.LC_REPORT, size=(200, -1))

        self.resultlst.InsertColumn(0, "Formula", format=wx.LIST_FORMAT_LEFT, width=100)
        self.resultlst.InsertColumn(1, "Mass [g]", format=wx.LIST_FORMAT_RIGHT, width=140)

        self.rescalealllst.InsertColumn(0, "Formula", format=wx.LIST_FORMAT_LEFT, width=100)
        self.rescalealllst.InsertColumn(1, "Scaled Mass [g]", format=wx.LIST_FORMAT_RIGHT, width=140)
        self.rescaletolst.InsertColumn(0, "Formula", format=wx.LIST_FORMAT_LEFT, width=100)
        self.rescaletolst.InsertColumn(1, "Scaled Mass [g]", format=wx.LIST_FORMAT_RIGHT, width=140)

        calculatebtn = wx.Button(self, label="Calculate")
        rescaleAllbtn = wx.Button(self, label="Rescale All")
        rescaleTobtn = wx.Button(self, label="Rescale To")

        # Layout

        fgs = wx.FlexGridSizer(rows=3, cols=3, hgap=10, vgap=10)

        fgs.AddGrowableCol(0)
        fgs.AddGrowableCol(1)
        fgs.AddGrowableCol(2)
        fgs.AddGrowableRow(1)

        fgs.Add(resulttxt, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT, border=10)
        fgs.Add(self.rescalealltxt, 0, wx.ALIGN_CENTER_HORIZONTAL)
        fgs.Add(self.rescaletotxt, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT, border=10)

        fgs.Add(self.resultlst, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.GROW|wx.LEFT, border=10)
        fgs.Add(self.rescalealllst, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.GROW)
        fgs.Add(self.rescaletolst, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.GROW|wx.RIGHT, border=10)

        fgs.Add(calculatebtn, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT, border=10)
        fgs.Add(rescaleAllbtn, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, border=10)
        fgs.Add(rescaleTobtn, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT, border=10)

        self.SetSizer(fgs)
        self.Fit()

        # Event Handlers

        calculatebtn.Bind(wx.EVT_BUTTON, main.OnCalculate)
        rescaleAllbtn.Bind(wx.EVT_BUTTON, main.OnRescaleAll)
        rescaleTobtn.Bind(wx.EVT_BUTTON, main.OnRescaleTo)

class MainFrame(wx.Frame):
    '''
    Main window of the program.
    '''

    def __init__(self, parent, id=wx.ID_ANY, title="",
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE,
                 name="MainFrame"):
        super(MainFrame, self).__init__(parent, id, title, pos, size, style,
                                        name)

        # Attributes

        # some color definition for nices display
        self.gray   = "#939393"

        self.columns = OrderedDict([
            ("id"      , column("Id", wx.LIST_FORMAT_LEFT, 50, "left", False)),
            ("name"    , column("Name", wx.LIST_FORMAT_LEFT, 200, "left", False)),
            ("formula" , column("Formula", wx.LIST_FORMAT_LEFT, 120, "left", False)),
            ("label"   , column("Label", wx.LIST_FORMAT_LEFT, 100, "left", False)),
            ("moles"   , column("Moles", wx.LIST_FORMAT_RIGHT, 90, "right", True)),
            ("conc"    , column("Concentration", wx.LIST_FORMAT_RIGHT, 100, "right", True)),
            ("molwt"   , column("Molecular Weight", wx.LIST_FORMAT_RIGHT, 120, "right", False)),
            ("short"   , column("Short name", wx.LIST_FORMAT_LEFT, 120, "left", False)),
            ("typ"     , column("Type", wx.LIST_FORMAT_LEFT, 100, "left", False)),
            ("reaction", column("Reaction", wx.LIST_FORMAT_LEFT, 200, "left", False)),
            ("cas"     , column("CAS No.", wx.LIST_FORMAT_RIGHT, 120, "left", False)),
        ])

        self.outlists = ["resultlst", "rescalealllst", "rescaletolst"]

        self.model = BatchCalculator()

        self.main_splitter = wx.SplitterWindow(self)
        self.inppanel = InputPanel(self.main_splitter, self)
        self.outpanel = OutputPanel(self.main_splitter, self)

        self.main_splitter.SplitHorizontally(self.inppanel, self.outpanel, sashPosition=250)

        # Menu

        menubar = wx.MenuBar()

        # File Menu
        filem = wx.Menu()
        mnew  = filem.Append(wx.ID_NEW, "&New\tCtrl+N", "New")
        filem.AppendSeparator()
        mopen = filem.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Open")
        msave = filem.Append(wx.ID_SAVE, "&Save\tCtrl+S", "Save")
        filem.AppendSeparator()
        metex = filem.Append(wx.ID_ANY, "Export TeX\t", "Export to a TeX file")
        filem.AppendSeparator()
        mexit = filem.Append(wx.ID_CLOSE, "Exit\tAlt+F4")
        menubar.Append(filem, "&File")
        # Edit Menu
        #editm = wx.Menu()
        #editm.Append(wx.ID_COPY, "Copy\tCtrl+C")
        #editm.Append(wx.ID_CUT, "Cut\tCtrl+X")
        #editm.Append(wx.ID_PASTE, "Paste\tCtrl+V")
        #menubar.Append(editm, "&Edit")
        # View Menu
        viewm = wx.Menu()
        mshowb = viewm.Append(wx.ID_ANY, "Show B Matrix")
        menubar.Append(viewm, "&View")
        # Database Menu
        dbm = wx.Menu()
        mchangedb = dbm.Append(wx.ID_ANY, "Change db\t", "Switch to a different database")
        menubar.Append(dbm, "Database")
        # About Menu
        aboutm = wx.Menu()
        about = aboutm.Append(wx.ID_ABOUT, "About")
        menubar.Append(aboutm, "&Help")
        self.SetMenuBar(menubar)

        # Event Handlers

        # Bind Menu Handlers
        self.Bind(wx.EVT_MENU, self.OnNew, mnew)
        self.Bind(wx.EVT_MENU, self.OnOpen, mopen)
        self.Bind(wx.EVT_MENU, self.OnSave, msave)
        self.Bind(wx.EVT_MENU, self.OnExit, mexit)
        self.Bind(wx.EVT_MENU, self.OnShowB, mshowb)
        self.Bind(wx.EVT_MENU, self.OnExportTex, metex)
        self.Bind(wx.EVT_MENU, self.OnChangeDB, mchangedb)
        self.Bind(wx.EVT_MENU, self.OnAbout, about)

    def OnNew(self, event):
        '''
        Start a new document by clearing all the lists
        '''

        # check if there is some results that might need saving
        if any(len(x) != 0 for x in [self.model.components,
                                     self.model.reactants]):
            dlg = wx.MessageDialog(self, 'There are unsaved changes, Save now?',
                                'Save',
                                wx.YES_NO | wx.CANCEL | wx.ICON_WARNING
                                )
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                self.OnSave(-1)
                self.ClearAllListCtrls()
                self.model.reset()
            elif result == wx.ID_NO:
                self.ClearAllListCtrls()
                self.model.reset()
            else:
                event.Skip()

            dlg.Destroy()

    def ClearAllListCtrls(self):
        '''
        Clear all the ListCtrls in the input and output panels.
        '''

        for attr in self.outlists:
            getattr(self.outpanel, attr).DeleteAllItems()

    def OnOpen(self, evt):
        '''
        Open the open file dialog.
        '''

        wildcard = "ZBC Files (*.zbc)|*.zbc|"     \
                   "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )

        dlg.SetFilterIndex(0)

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            path = dlg.GetPath()

            # open the file and read the actual data
            fp = open(path, 'rb')
            (self.model.components, self.model.reactants,\
            self.model.A, self.model.B, self.model.X,\
            self.model.scale_all, self.model.sample_scale,\
            self.model.sample_size, self.model.selections) = pickle.load(fp)

            fp.close()

            # clear all the lists with the inputs
            self.ClearAllListCtrls()

            for obj in self.model.components:
                if obj.category == "zeolite":
                    self.inppanel.zeolst.Append([obj.listctrl_label(), "{0:>8.2f}".format(obj.moles)])
                elif obj.category == "template":
                    self.inppanel.tmplst.Append([obj.listctrl_label(), "{0:>8.2f}".format(obj.moles)])
                elif obj.category == "zgm":
                    self.inppanel.zgmlst.Append([obj.listctrl_label(), "{0:>8.2f}".format(obj.moles)])
            for obj in self.model.reactants:
                self.inppanel.rctlst.Append([obj.listctrl_label(), "{0:>8.2f}".format(obj.concentration)])

            for obj in self.model.reactants:
                self.outpanel.resultlst.Append([obj.listctrl_label(), "{0:10.4f}".format(obj.mass)])
            rescaled = self.model.rescale_all()
            for subs, mass in rescaled:
                self.outpanel.rescalealllst.Append([subs.listctrl_label(), "{0:10.4f}".format(mass)])
            rescaled = self.model.rescale_to(self.model.selections)
            for i, (obj, mass) in enumerate(rescaled):
                self.outpanel.rescaletolst.Append([obj.listctrl_label(), "{0:10.4f}".format(mass)])
                if i in self.model.selections:
                        self.outpanel.rescaletolst.SetItemBackgroundColour(i, self.gray)

        dlg.Destroy()

    def OnSave(self, event):
        '''
        Open the save file dialog.
        '''

        wildcard = "ZBC Files (*.zbc)|*.zbc|"     \
                   "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(),
            defaultFile="", wildcard=wildcard, style=wx.SAVE|wx.OVERWRITE_PROMPT
            )

        # This sets the default filter that the user will initially see. Otherwise,
        # the first filter in the list will be used by default.
        dlg.SetFilterIndex(0)

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if not os.path.splitext(path)[1] == '.zbc':
                path += '.zbc'

            data = (self.model.components,
                    self.model.reactants,
                    self.model.A, self.model.B, self.model.X,
                    self.model.scale_all, self.model.sample_scale,
                    self.model.sample_size, self.model.selections)
            fp = file(path, 'wb') # Create file anew
            pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)
            fp.close()

        dlg.Destroy()

    def OnExportTex(self, event):
        '''
        Open the dialog with options about the TeX document tobe written.
        '''
        etexdialog = ExportTexDialog(parent=self, id=-1)
        result = etexdialog.ShowModal()
        if result == wx.ID_OK:
            flags = etexdialog.GetData()
            # get the string with contents of the TeX report
            tex = get_report_as_string(flags, self.model)
            self.OnSaveTeX(tex, flags['typeset'], flags['pdflatex'])

    def OnSaveTeX(self, texdata, typeset, pdflatex):

        texwildcard =  "TeX Files (*.tex)|*tex|"     \
                       "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(),
            defaultFile="", wildcard=texwildcard, style=wx.SAVE|wx.OVERWRITE_PROMPT
            )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if not os.path.splitext(path)[1] == '.tex':
                path += '.tex'

            fp = file(path, 'w') # Create file anew
            fp.write(texdata)
            fp.close()

            if typeset:
                if pdflatex is not None:
                    os.chdir(os.path.split(path)[0])
                    p = subprocess.Popen([pdflatex, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    out, err = p.communicate()
                    if p.returncode != 0:
                        dlg = wx.MessageDialog(None, "There were problems generating the pdf, check the log file:\n{0}".format(err),
                                                "", wx.OK | wx.ICON_WARNING)
                        dlg.ShowModal()
                        dlg.Destroy()
                    else:
                        # run again and clean the auxiliary files
                        p = subprocess.Popen([pdflatex, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        out, err = p.communicate()
                        clean_tex(path)
                else:
                    dlg = wx.MessageDialog(None, "pdflatex not foudn, pdf not generated",
                                            "", wx.OK | wx.ICON_WARNING)
                    dlg.ShowModal()
                    dlg.Destroy()

    def OnExit(self, event):
        self.Close()

    def OnShowB(self, event):

        if isinstance(self.model.B, list):
            dlg = wx.MessageDialog(None, "Batch Matrix needs to be defined first.",
                                    "", wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        elif type(self.model.B).__module__ == np.__name__:
            frame = ShowBFrame(self, sys.stdout)
            frame.Show(True)

    def OnAbout(self, event):
        '''
        Show the about dialog
        '''

        info = wx.AboutDialogInfo()
        info.SetName("Zeolite Batch Calculator")
        info.SetVersion(__version__)
        info.SetCopyright("Copyright (C) Lukasz Mentel")
        info.SetDescription(wordwrap('''A GUI script based on wxPython for calculating \
the correct amount of reagents (batch) for a particular zeolite composition \
given by the molar ratio of its components.''', 350, wx.ClientDC(self)))

        info.WebSite = ("https://github.com/lmmentel/batchcalculator", "ZBC Code Repository")
        info.Developers = ["Katarzyna Lukaszuk"]
        #info.License = wordwrap(__doc__, 600, wx.ClientDC(self))

        wx.AboutBox(info)

    def OnCalculate(self, event):

        self.model.calculate()

        self.outpanel.resultlst.DeleteAllItems()

        for i, reac in enumerate(self.model.reactants):
            self.outpanel.resultlst.Append([reac.listctrl_label(), "{0:10.4f}".format(reac.mass)])

    def OnRescaleAll(self, event):
        '''
        Retrieve a float from a TextCtrl dialog, rescale the result and print
        it to the ListCtrl.
        '''

        dialog = wx.TextEntryDialog(None,
            "Enter the scaling factor",
            "Enter the scaling factor", str(self.model.scale_all), style=wx.OK|wx.CANCEL)
        if dialog.ShowModal() == wx.ID_OK:
            try:
                self.model.scale_all = float(dialog.GetValue())

                self.outpanel.rescalealllst.DeleteAllItems()

                rescaled = self.model.rescale_all()
                for i, (subs, mass) in enumerate(rescaled):
                    self.outpanel.rescalealllst.Append([subs.listctrl_label(), "{0:10.4f}".format(mass)])
                self.outpanel.rescalealltxt.SetLabel("Rescaled by {0:8.3f}".format(self.model.scale_all))
                self.outpanel.Layout()
            except:
                ed = wx.MessageDialog(None, "Scale factor must be a number",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()
        dialog.Destroy()

    def OnRescaleTo(self, event):
        '''
        Retrieve thescaling afctor and selections from a custom dialog, then
        calculate the scaling factor so that the selected item after rescaling
        sum up to the sample size. Use the scaling factor to rescale all the
        items and print them to the ListCtrl.
        '''

        rto = RescaleToDialog(self, self.model, -1, title="Choose substances and sample size")
        result = rto.ShowModal()
        if result == wx.ID_OK:
            # get the sample size and sample selections
            try:
                sample_size, sample_selections = rto.GetCurrentSelections()
                self.model.sample_size = float(sample_size)
                self.model.selections = sample_selections

                self.outpanel.rescaletolst.DeleteAllItems()

                rescaled = self.model.rescale_to(sample_selections)

                for i, (subs, mass) in enumerate(rescaled):
                    self.outpanel.rescaletolst.Append([subs.listctrl_label(), "{0:10.4f}".format(mass)])
                    if i in sample_selections:
                        self.outpanel.rescaletolst.SetItemBackgroundColour(i, self.gray)
                self.outpanel.rescaletotxt.SetLabel("Rescaled to {0:8.3f} [g]".format(self.model.sample_size))
                self.outpanel.Layout()
            except:
                self.sample_size = 5.0
                ed = wx.MessageDialog(None, "Scale factor must be a number",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()

    def OnChangeDB(self, event):
        '''
        Diplay the file dialog to choose the new database to be used
        then establish the db session in the model (BatchCalculator).
        '''

        dbwildcard = "db Files (*.db)|*.db|"     \
                     "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message="Choose database file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=dbwildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.model.new_dbsession(path)
        dlg.Destroy()


class ExceptionDialog(GMD.GenericMessageDialog):
    def __init__(self, msg):
        '''Constructor'''
        GMD.GenericMessageDialog.__init__(self, None, msg, "Exception!",
                                              wx.OK|wx.ICON_ERROR)

def ExceptionHook(exctype, value, trace):
    '''
    Handler for all unhandled exceptions

    Args:
        exctype: Exception Type
        value: Error Value
        trace: Trace back info
    '''

    frame = wx.GetApp().GetTopWindow()
    # Format the traceback
    exc = traceback.format_exception(exctype, value, trace)
    ftrace = "".join(exc)
    app = wx.GetApp()
    msg = "An unexpected error has occurred: %s" % ftrace
    dlg = ExceptionDialog(msg)
    dlg.ShowModal()
    dlg.Destroy()

class ZeoGui(wx.App):

    def OnInit(self):

        self.frame = MainFrame(None, title="Zeolite Batch Calculator",
                               size=(860, 550))
        # change the default exception handling
        sys.excepthook = ExceptionHook
        self.SetTopWindow(self.frame)
        self.frame.Show()

        return True

if __name__ == "__main__":

    app = ZeoGui(False)
    # uncomment for debugging
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
