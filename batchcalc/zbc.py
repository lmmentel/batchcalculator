# file: zbc.py
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


import os
import pickle
import subprocess
import sys
import traceback

import numpy as np

import wx
import wx.grid as gridlib
from wx.lib.wordwrap import wordwrap

from ObjectListView import ObjectListView

from batchcalc.tex_writer import get_report_as_string
from batchcalc.pdf_writer import create_pdf, create_pdf_composition
from batchcalc.calculator import BatchCalculator
from batchcalc import controller as ctrl
from batchcalc import dialogs

from batchcalc.utils import get_columns


__version__ = "0.2.1"

# uncomment for debugging
# import wx.lib.inspection


def clean_tex(fname):
    '''Clean the auxiliary tex files.'''

    exts = [".out", ".aux", ".log"]
    fbase = os.path.splitext(fname)[0]
    for fil in [fbase + ext for ext in exts]:
        if os.path.exists(fil):
            os.remove(fil)


class AddModifyDBBaseFrame(wx.Frame):
    def __init__(self, parent, cols=None, id=wx.ID_ANY, title="Edit Database",
                 pos=wx.DefaultPosition, size=(500, 300),
                 style=wx.DEFAULT_FRAME_STYLE, name=""):

        super(AddModifyDBBaseFrame, self).__init__(parent, id, title, pos, size, style, name)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)

        self.olv = ObjectListView(self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.olv.evenRowsBackColor = "#DCF0C7"
        self.olv.oddRowsBackColor = "#FFFFFF"
        self.olv.SetEmptyListMsg("No Records Found")

        # create the button row
        addRecordBtn = wx.Button(self, label="Add")
        addRecordBtn.Bind(wx.EVT_BUTTON, self.onAddRecord)
        btnSizer.Add(addRecordBtn, 0, wx.ALL, 5)

        editRecordBtn = wx.Button(self, label="Edit")
        editRecordBtn.Bind(wx.EVT_BUTTON, self.onEditRecord)
        btnSizer.Add(editRecordBtn, 0, wx.ALL, 5)

        deleteRecordBtn = wx.Button(self, label="Delete")
        deleteRecordBtn.Bind(wx.EVT_BUTTON, self.onDelete)
        btnSizer.Add(deleteRecordBtn, 0, wx.ALL, 5)

        showAllBtn = wx.Button(self, label="Show All")
        showAllBtn.Bind(wx.EVT_BUTTON, self.onShowAllRecords)
        btnSizer.Add(showAllBtn, 0, wx.ALL, 5)

        mainSizer.Add(self.olv, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(btnSizer, 0, wx.CENTER)
        self.SetSizer(mainSizer)

    def onAddRecord(self, event):
        '''Add a record to the database'''

        print "adding"

    def onEditRecord(self, event):
        '''Edit a record'''

        print "editing"

    def onDelete(self, event):
        '''Delete a record'''

        print "deleting"

    def onSearch(self, event):
        """
        Searches database based on the user's filter choice and keyword
        """
        print "searching"

    def onShowAllRecords(self, event):
        '''Updates the record list to show all of them'''

        print "showing all"


class AddModifyBatchTableFrame(AddModifyDBBaseFrame):

    def __init__(self, parent, session, **kwargs):

        super(AddModifyBatchTableFrame, self).__init__(parent, **kwargs)

        # attributes

        self.model = parent.model
        self.cols = ["id", "chemical", "component", "coeff", "reaction"]
        self.session = session

        self.show_all()

    def onAddRecord(self, event):
        """
        Add a record to the database
        """

        dlg = ctrl.AddModifyBatchRecordDialog(self, session=self.session,
                                              title="Add",
                                              add_record=True)
        dlg.ShowModal()
        dlg.Destroy()
        self.show_all()

    def onEditRecord(self, event):
        """
        Edit a record
        """

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        dlg = ctrl.AddModifyBatchRecordDialog(self, session=self.session,
                                              record=sel_row,
                                              title="Modify",
                                              add_record=False)
        result = dlg.ShowModal()
        dlg.Destroy()
        self.show_all()

    def onDelete(self, event):
        '''Delete a record'''

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        ctrl.delete_batch_record(self.session, sel_row.id)
        self.show_all()

    def onShowAllRecords(self, event):
        '''Update the record list to show all of them'''

        self.show_all()

    def set_olv(self, batches):
        '''Put current Batch objects in the OLV'''

        olv_cols = get_columns(self.cols)
        self.olv.SetColumns(olv_cols)
        self.olv.SetObjects(batches)

    def show_all(self):
        '''Get all batch records and put them in the OLV'''

        batches = ctrl.get_batches(self.session)
        self.set_olv(batches)


class AddModifyChemicalTableFrame(AddModifyDBBaseFrame):

    def __init__(self, parent, session, **kwargs):

        super(AddModifyChemicalTableFrame, self).__init__(parent, **kwargs)

        # attributes

        self.model = parent.model
        self.cols = ["id", "name", "formula", "conc", "molwt", "short", "kind",
                     "physform", "elect", "cas", "pk", "density", "smiles"]
        self.session = session

        self.show_all()

    def onAddRecord(self, event):
        '''Add a record to the database'''

        dlg = ctrl.AddModifyChemicalRecordDialog(self, session=self.session,
                                                 title="Add",
                                                 add_record=True)
        dlg.ShowModal()
        dlg.Destroy()
        self.show_all()

    def onEditRecord(self, event):
        '''Edit a record'''

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        dlg = ctrl.AddModifyChemicalRecordDialog(self, session=self.session,
                                                 record=sel_row,
                                                 title="Modify",
                                                 add_record=False)
        result = dlg.ShowModal()
        dlg.Destroy()
        self.show_all()

    def onDelete(self, event):
        '''Delete a record'''

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        ctrl.delete_chemical_record(self.session, sel_row.id)
        self.show_all()

    def onShowAllRecords(self, event):
        '''Updates the record list to show all of them'''

        self.show_all()

    def set_olv(self, chemicals):
        '''Put current Chemical objects in the OLV'''

        olv_cols = get_columns(self.cols)
        self.olv.SetColumns(olv_cols)
        self.olv.SetObjects(chemicals)

    def show_all(self):
        '''Get all chemical records and put them in the OLV'''

        chemicals = ctrl.get_chemicals(self.session, components=None,
                                       showall=True)
        self.set_olv(chemicals)


class AddModifyComponentTableFrame(AddModifyDBBaseFrame):

    def __init__(self, parent, session, **kwargs):

        super(AddModifyComponentTableFrame, self).__init__(parent, **kwargs)

        # attributes

        self.model = parent.model
        self.cols = ["id", "name", "formula", "molwt", "short", "category"]
        self.session = session

        self.show_all()

    def onAddRecord(self, event):
        '''Add a record to the database'''

        dlg = ctrl.AddModifyComponentRecordDialog(self, session=self.session,
                                                  title="Add",
                                                  add_record=True)
        dlg.ShowModal()
        dlg.Destroy()
        self.show_all()

    def onEditRecord(self, event):
        '''Edit a record'''

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")

            return
        dlg = ctrl.AddModifyComponentRecordDialog(self, session=self.session,
                                                  record=sel_row,
                                                  title="Modify",
                                                  add_record=False)
        result = dlg.ShowModal()
        dlg.Destroy()
        self.show_all()

    def onDelete(self, event):
        '''Delete a record'''

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        ctrl.delete_component_record(self.session, sel_row.id)
        self.show_all()

    def onSearch(self, event):
        """
        Searches database based on the user's filter choice and keyword
        """

        pass

    def onShowAllRecords(self, event):
        '''Updates the record list to show all of them'''

        self.show_all()

    def set_olv(self, components):
        '''Put current Component objects in the OLV'''

        olv_cols = get_columns(self.cols)
        self.olv.SetColumns(olv_cols)
        self.olv.SetObjects(components)

    def show_all(self):
        '''Get all component records and put them in the OLV'''

        components = ctrl.get_components(self.session)
        self.set_olv(components)

class AddModifyCategoryTableFrame(AddModifyDBBaseFrame):

    def __init__(self, parent, session, **kwargs):

        super(AddModifyCategoryTableFrame, self).__init__(parent, **kwargs)

        # attributes

        self.model = parent.model
        self.cols = ["id", "categobj"]
        self.session = session

        self.show_all()

    def onAddRecord(self, event):
        '''Add a record to the database'''

        dlg = wx.TextEntryDialog(None,
            "Enter new category",
            "Enter new category", "", style=wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            category = dlg.GetValue()
            if category != "":
                ctrl.add_category_record(self.session, category)
            else:
                ed = wx.MessageDialog(None, "Nothing entered",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()
        dlg.Destroy()
        self.show_all()

    def onEditRecord(self, event):
        '''Edit a record'''

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return

        dlg = wx.TextEntryDialog(None,
            "Enter the category",
            "Enter the category", sel_row.name, style=wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            category = dlg.GetValue()
            if category != "":
                ctrl.modify_category_record(self.session, sel_row.id, category)
            else:
                ed = wx.MessageDialog(None, "Nothing entered",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()
        dlg.Destroy()
        self.show_all()

    def onDelete(self, event):
        '''Delete a record'''

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        ctrl.delete_category_record(self.session, sel_row.id)
        self.show_all()

    def onShowAllRecords(self, event):
        '''Updates the record list to show all of them'''

        self.show_all()

    def set_olv(self, categories):
        '''Put current Category objects in the OLV'''

        olv_cols = get_columns(self.cols)
        self.olv.SetColumns(olv_cols)
        self.olv.SetObjects(categories)

    def show_all(self):
        '''Get all category records and put them in the OLV'''

        categories = ctrl.get_categories(self.session)
        self.set_olv(categories)


class AddModifyReactionTableFrame(AddModifyDBBaseFrame):

    def __init__(self, parent, session, **kwargs):

        super(AddModifyReactionTableFrame, self).__init__(parent, **kwargs)

        # attributes

        self.model = parent.model
        self.cols = ["id", "reaction"]
        self.session = session
        self.show_all()

    def onAddRecord(self, event):
        '''Add a record to the database'''

        dlg = wx.TextEntryDialog(None,
            "Enter the reaction",
            "Enter the reaction", "", style=wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            reaction = dlg.GetValue()
            if reaction != "":
                ctrl.add_reaction_record(self.session, reaction)
            else:
                ed = wx.MessageDialog(None, "Nothing entered",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()
        dlg.Destroy()
        self.show_all()

    def onEditRecord(self, event):
        '''Edit a record'''

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return

        dlg = wx.TextEntryDialog(None,
            "Enter the reaction",
            "Enter the reaction", sel_row.reaction, style=wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            reaction = dlg.GetValue()
            if reaction != "":
                ctrl.modify_reaction_record(self.session, sel_row.id, reaction)
            else:
                ed = wx.MessageDialog(None, "Nothing entered",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()
        dlg.Destroy()
        self.show_all()

    def onDelete(self, event):
        '''Delete a record'''

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        ctrl.delete_reaction_record(self.session, sel_row.id)
        self.show_all()

    def onShowAllRecords(self, event):
        '''Updates the record list to show all of them'''

        self.show_all()

    def set_olv(self, reactions):
        '''Put current Reaction objects in the OLV'''

        olv_cols = get_columns(self.cols)
        self.olv.SetColumns(olv_cols)
        self.olv.SetObjects(reactions)

    def show_all(self):
        '''Get all reaction records and put them in the OLV'''

        reactions = ctrl.get_reactions(self.session)
        self.set_olv(reactions)


class ShowBFrame(wx.Frame):
    def __init__(self, parent, log, id=wx.ID_ANY, title="Batch Matrix",
                 pos=wx.DefaultPosition, size=(500, 300),
                 style=wx.DEFAULT_FRAME_STYLE,
                 name="Show Batch Matrix Dialog"):

        super(ShowBFrame, self).__init__(parent, id, title, pos, size, style,
                                         name)

        panel = wx.Panel(self, -1, style=0)
        grid = CustTableGrid(panel, parent.model)
        okbtn = wx.Button(panel, wx.ID_OK)
        okbtn.Bind(wx.EVT_BUTTON, self.OnOKButton)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.GROW | wx.ALL, 5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(okbtn)
        sizer.Add(hbox, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)
        panel.SetSizer(sizer)

    def OnOKButton(self, evt):
        self.Close()

    def OnButtonFocus(self, evt):
        pass


class ShowSynthesesFrame(wx.Frame):

    def __init__(self, parent, session, cols=None, id=wx.ID_ANY,
                 title="Syntheses", pos=wx.DefaultPosition, size=(600, 400),
                 style=wx.DEFAULT_FRAME_STYLE, name="Syntheses"):

        super(ShowSynthesesFrame, self).__init__(parent, id, title, pos,
                                                 size, style, name)

        # attributes

        self.cols = ["id", "name", "target", "laborant", "reference",
                     "temperature", "descr"]

        self.session = session
        self.model = BatchCalculator()

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.olv = ObjectListView(self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.olv.evenRowsBackColor = "#DCF0C7"
        self.olv.oddRowsBackColor = "#FFFFFF"
        self.olv.SetEmptyListMsg("No Records Found")

        # create the button row

        loadRecordBtn = wx.Button(self, label="Load")
        loadRecordBtn.Bind(wx.EVT_BUTTON, self.onLoadRecord)
        btnSizer.Add(loadRecordBtn, 0, wx.ALL, 5)

        editRecordBtn = wx.Button(self, label="Edit")
        editRecordBtn.Bind(wx.EVT_BUTTON, self.onEditRecord)
        btnSizer.Add(editRecordBtn, 0, wx.ALL, 5)

        deleteRecordBtn = wx.Button(self, label="Delete")
        deleteRecordBtn.Bind(wx.EVT_BUTTON, self.onDelete)
        btnSizer.Add(deleteRecordBtn, 0, wx.ALL, 5)

        exportRecordBtn = wx.Button(self, label="Export")
        exportRecordBtn.Bind(wx.EVT_BUTTON, self.onExportRecord)
        btnSizer.Add(exportRecordBtn, 0, wx.ALL, 5)

        cancelBtn = wx.Button(self, label="Cancel")
        cancelBtn.Bind(wx.EVT_BUTTON, self.OnCloseFrame)
        self.Bind(wx.EVT_CLOSE, self.OnCloseFrame)
        btnSizer.Add(cancelBtn, 0, wx.ALL, 5)

        mainSizer.Add(self.olv, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(btnSizer, 0, wx.CENTER)
        self.SetSizerAndFit(mainSizer)

        self.show_all()

    def onEditRecord(self, event):
        'Edit a record'

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return

        dlg = ctrl.AddModifySynthesisRecordDialog(parent=self,
                                                  model=self.model,
                                                  session=self.session,
                                                  record=sel_row,
                                                  title="Modify",
                                                  add_record=False)
        result = dlg.ShowModal()
        dlg.Destroy()
        self.show_all()

    def onExportRecord(self, event):
        'Add a record to the database'

        # TODO: finish this

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return

        print "exporting synthesis: ", sel_row

    def onDelete(self, event):
        '''Delete a synthesis record'''

        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        ctrl.delete_synthesis_record(self.session, sel_row.id)
        self.show_all()

    def onLoadRecord(self, event):
        'Load a record into the batch calculator'

        # reset the calcualtor state
        sel_row = self.olv.GetSelectedObject()
        parent = self.GetParent()
        if sel_row is not None:
            # add component to the main frame
            components = [c.component for c in sel_row.components]
            for comp, synthcomp in zip(components, sel_row.components):
                comp.moles = synthcomp.moles
            parent.model.components = components
            parent.inppanel.comp_olv.SetObjects(parent.model.components)
            # add chemicals to the main frame
            chemicals = [c.chemical for c in sel_row.chemicals]
            for chem, synthchem in zip(chemicals, sel_row.chemicals):
                chem.mass = synthchem.mass
            parent.model.chemicals = chemicals
            parent.inppanel.chem_olv.SetObjects(parent.model.chemicals)
        else:
            dialogs.show_message_dlg("No row selected", "Error")
            return

    def OnCloseFrame(self, event):
        '''Close the synthesis frame'''

        self.Destroy()

    def set_olv(self, syntheses):
        '''Put current Synthesis objects in the OLV'''

        olv_cols = get_columns(self.cols)
        self.olv.SetColumns(olv_cols)
        self.olv.SetObjects(syntheses)

    def show_all(self):
        '''Get all synthesis records and put them in the OLV'''

        syntheses = ctrl.get_syntheses(self.session)
        self.set_olv(syntheses)


class CustomDataTable(gridlib.PyGridTableBase):
    def __init__(self, model):
        gridlib.PyGridTableBase.__init__(self)

        self.col_labels = [x.listctrl_label() for x in model.components]
        self.row_labels = [x.listctrl_label() for x in model.chemicals]

        self.data_types = [gridlib.GRID_VALUE_FLOAT] * len(model.chemicals)

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
        # table and will destroy it when done.  Otherwise you would need to
        # keep a reference to it and call it's Destroy method later.
        self.SetTable(table, True)

        # self.SetRowLabelSize(0)
        self.SetMargins(5, 5)
        self.AutoSizeColumns(True)
        for i in range(self.GetNumberRows()):
            self.SetColFormatFloat(i, width=10, precision=4)
        self.SetRowLabelSize(200)

        gridlib.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)

    # I do this because I don't like the default behaviour of not starting the
    # cell editor on double clicks, but only a second click.
    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()


def compRowFormatter(listItem, Component):
    red = "#FF6B66"
    yellow = "#FFDE66"
    orange = "#FF9166"
    green = "#D4FF66"
    gray = "#939393"

    if Component.category == "zeolite":
        listItem.SetBackgroundColour(red)
    elif Component.category == "template":
        listItem.SetBackgroundColour(yellow)
    elif Component.category == "zgm":
        listItem.SetBackgroundColour(orange)


class InputPanel(wx.Panel):

    def __init__(self, parent, session, model):
        super(InputPanel, self).__init__(parent, style=wx.SUNKEN_BORDER)

        # Attributes

        self.model = model
        self.session = session

        self.tw = wx.GetTopLevelParent(parent)

        self.comp_cols = ["name", "formula", "molwt", "short", "category"]
        self.chem_cols = ["name", "formula", "conc", "molwt", "short", "kind",
                          "physform", "cas"]

        cmptxt = wx.StaticText(self, -1, label="Components")
        rcttxt = wx.StaticText(self, -1, label="Chemicals")
        cmptxt.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        rcttxt.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.comp_olv = ObjectListView(self, wx.ID_ANY,
                                       style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.comp_olv.SetEmptyListMsg('Add Components')
        self.comp_olv.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
        self.comp_olv.rowFormatter = compRowFormatter

        self.chem_olv = ObjectListView(self, wx.ID_ANY,
                                       style=wx.LC_REPORT | wx.SUNKEN_BORDER,
                                       useAlternateBackColors=True)
        self.chem_olv.SetEmptyListMsg('Add Chemicals')
        self.chem_olv.evenRowsBackColor = "#DCF0C7"
        self.chem_olv.oddRowsBackColor = "#FFFFFF"
        self.chem_olv.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK

        self.SetComponents()
        self.SetChemicals()
        zeobtn = wx.Button(self, -1, label="Add/Remove")
        rctbtn = wx.Button(self, -1, label="Add/Remove")

        # Layout

        gbs = wx.GridBagSizer(hgap=10, vgap=10)

        gbs.Add(cmptxt, pos=(0, 0), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP,
                border=5)
        gbs.Add(rcttxt, pos=(0, 1), flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP,
                border=5)

        gbs.Add(self.comp_olv, pos=(1, 0),
                flag=wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.LEFT,
                border=10)
        gbs.Add(self.chem_olv, pos=(1, 1),
                flag=wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.RIGHT,
                border=10)

        gbs.Add(zeobtn, pos=(2, 0),
                flag=wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, border=5)
        gbs.Add(rctbtn, pos=(2, 1),
                flag=wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, border=5)

        self.SetSizerAndFit(gbs)
        gbs.AddGrowableCol(0)
        gbs.AddGrowableCol(1)
        gbs.AddGrowableRow(1)
        self.Layout()

        # Event Handlers

        zeobtn.Bind(wx.EVT_BUTTON, self.OnAddRemoveComponents)
        rctbtn.Bind(wx.EVT_BUTTON, self.OnAddRemoveChemicals)

    def OnAddRemoveComponents(self, event):
        '''
        Show the dialog with the zeolite components retrieved from the
        database.
        '''

        self.dlg = ctrl.ComponentsDialog(self, self.session, self.model,
                    cols=get_columns(self.comp_cols),
                    id=-1, title="Choose Zeolite Components...")
        result = self.dlg.ShowModal()
        if result == wx.ID_OK:
            self.model.components = self.dlg.GetCurrentSelections()
        self.comp_olv.SetObjects(self.model.components)
        self.dlg.Destroy()

    def OnAddRemoveChemicals(self, event):
        '''
        Show the dialog with the chemicals retrieved from the database.
        '''

        self.dlg = ctrl.ChemicalsDialog(self, self.session, self.model,
                    cols=get_columns(self.chem_cols),
                    id=-1, title="Choose Chemicals...")
        result = self.dlg.ShowModal()
        if result == wx.ID_OK:
            self.model.chemicals = self.dlg.GetCurrentSelections()
        self.chem_olv.SetObjects(self.model.chemicals)
        self.dlg.Destroy()

    def SetComponents(self):
        '''Set the OLV columns and put current Component objects in the OLV'''

        olv_cols = get_columns(["label", "moles"])
        self.comp_olv.SetColumns(olv_cols)
        self.comp_olv.SetObjects(self.model.components)

    def SetChemicals(self):
        '''Set the OLV columns and put current Chemical objects in the OLV'''

        olv_cols = get_columns(["label", "conc"])
        self.chem_olv.SetColumns(olv_cols)
        self.chem_olv.SetObjects(self.model.chemicals)


class MolesInputPanel(InputPanel):
    '''
    Input panel for the inverse calculation masses -> moles
    '''

    def __init__(self, parent, session, model):
        super(MolesInputPanel, self).__init__(parent, session, model)

    def SetComponents(self):
        '''Set the OLV columns and put current Component objects in the OLV'''

        olv_cols = get_columns(["label"])
        self.comp_olv.SetColumns(olv_cols)
        self.comp_olv.SetObjects(self.model.components)

    def SetChemicals(self):
        '''Set the OLV columns and put current Chemical objects in the OLV'''

        olv_cols = get_columns(["label", "mass", "conc"])
        olv_cols[1].isEditable = True
        self.chem_olv.SetColumns(olv_cols)
        self.chem_olv.SetObjects(self.model.chemicals)


class OutputPanel(wx.Panel):

    def __init__(self, parent, session, model):
        super(OutputPanel, self).__init__(parent, style=wx.SUNKEN_BORDER)

        # Attributes

        self.session = session
        self.model = model
        self.gray  = "#939393"

        resulttxt = wx.StaticText(self, -1, label="Results")
        resulttxt.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.resultOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER,
                useAlternateBackColors=True)
        self.resultOlv.evenRowsBackColor="#DCF0C7"
        self.resultOlv.oddRowsBackColor="#FFFFFF"

        calculateBtn = wx.Button(self, label="Calculate")

        scaling_title = wx.StaticBox( self, -1, "Scaling options" )
        scaling_box = wx.StaticBoxSizer( scaling_title, wx.VERTICAL )

        self.scaling_ctrls = []
        scalenone = wx.RadioButton(self, -1, label="No scaling", style=wx.RB_GROUP)
        scaleall = wx.RadioButton(self, -1, label="Scale all")
        scalesample = wx.RadioButton(self, -1, label="Scale to sample")
        scaleitem = wx.RadioButton(self, -1, label="Scale to item")

        sn_text = wx.StaticText(self, -1, label="", size=(100, 20), style=wx.ALIGN_RIGHT)
        sa_text = wx.StaticText(self, -1, label="", size=(70, 20), style=wx.ALIGN_RIGHT)
        ss_text = wx.StaticText(self, -1, label="", size=(70, 20), style=wx.ALIGN_RIGHT)
        si_text = wx.StaticText(self, -1, label="", size=(70, 20), style=wx.ALIGN_RIGHT)

        self.scaling_ctrls.append(("none", scalenone, sn_text))
        self.scaling_ctrls.append(("all", scaleall, sa_text))
        self.scaling_ctrls.append(("sample", scalesample, ss_text))
        self.scaling_ctrls.append(("item", scaleitem, si_text))

        scaling_grid = wx.FlexGridSizer( cols=2 )
        for label, radio, text in self.scaling_ctrls:
            scaling_grid.Add( radio, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
            scaling_grid.Add( text, 0, wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

        scaling_box.Add(scaling_grid)

        self.SetResults()

        # Layout

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        gbs = wx.GridBagSizer(hgap=10, vgap=10)

        gbs.Add(resulttxt, pos=(0, 0), span=(1, 2), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.TOP, border=5)

        gbs.Add(self.resultOlv, pos=(1, 0), span=(2, 1), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.GROW|wx.LEFT|wx.BOTTOM, border=10)
        gbs.Add(scaling_box, pos=(1, 1), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.GROW|wx.LEFT|wx.RIGHT, border=10)

        gbs.Add(calculateBtn, pos=(2, 1), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_BOTTOM|wx.BOTTOM|wx.LEFT, border=10)

        gbs.AddGrowableCol(0)
        #gbs.AddGrowableCol(1)
        gbs.AddGrowableRow(1)

        self.SetSizerAndFit(gbs)

        # Event Handlers

        calculateBtn.Bind(wx.EVT_BUTTON, self.OnCalculate)

        # set default as no scaling
        scalenone.SetValue(1)
        for label, radio, text in self.scaling_ctrls[1:]:
            radio.SetValue(0)

    def OnCalculate(self, event):
        '''
        Calculate the masses of chemicals in the batch and display the
        result in the OLV.
        '''

        # get the checked radio control label and StaticText object
        scale_type, text = next((x[0], x[2]) for x in self.scaling_ctrls if x[1].GetValue())

        self.model.calculate_masses(self.session)

        if scale_type == 'none':
            pass
        elif scale_type == 'all':
            self.rescale_all(text)
        elif scale_type == 'sample':
            self.rescale_to_sample(text)
        elif scale_type == 'item':
            self.rescale_to_item(text)
        else:
            raise ValueError('wrong <scale_type>: {}'.format(scale_type))

        self.resultOlv.SetObjects(self.model.chemicals)
        self.Layout()

    def rescale_all(self, statictext):
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
            except:
                ed = wx.MessageDialog(None, "Scale factor must be a number",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()
            newmasses = self.model.rescale_all()
            for chemical, newmass in zip(self.model.chemicals, newmasses):
                chemical.mass = newmass
            statictext.SetLabel("{0:6.2f}".format(self.model.scale_all))
        dialog.Destroy()

    def rescale_to_item(self, statictext):
        '''
        Retrieve the selected item and the mass for that item to which it
        should be scaled, then rescale all the components and display them.
        '''

        rtsd = dialogs.RescaleToItemDialog(self, self.model.chemicals,
                cols=get_columns(["label", "mass"]),
                title="Choose chemical and desired mass")

        result = rtsd.ShowModal()
        if result == wx.ID_OK:
            mass, item = rtsd.GetCurrentSelections()
            try:
                mass = float(mass)
            except:
                mass = 1.0
                ed = wx.MessageDialog(None, "Mass must be a number",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()

            if len(item) == 0 or len(item) > 1:
                dlg = wx.MessageDialog(None, "Precisely one item has to be selected.",
                                       "", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                newmasses = self.model.rescale_to_chemical(item[0], mass)
                for chemical, newmass in zip(self.model.chemicals, newmasses):
                    chemical.mass = newmass
                statictext.SetLabel("{0:6.2f}".format(mass))

    def rescale_to_sample(self, statictext):
        '''
        Retrieve the scaling factor and selections from a custom dialog, then
        calculate the scaling factor so that the selected item after rescaling
        sum up to the sample size. Use the scaling factor to rescale all the
        items and print them to the ListCtrl.
        '''

        rto = dialogs.RescaleToSampleDialog(self, self.model,
                cols=get_columns(["label", "mass"]),
                title="Choose chemicals and sample size")
        result = rto.ShowModal()
        if result == wx.ID_OK:
            # get the sample size and sample selections
            sample_size, selections = rto.GetCurrentSelections()
            try:
                self.model.sample_size = float(sample_size)
            except:
                self.sample_size = 5.0
                ed = wx.MessageDialog(None, "Scale factor must be a number",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()

            self.model.selections = selections
            if len(selections) == 0:
                dlg = wx.MessageDialog(None, "At least one reactant must be selected.",
                                       "", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                newmasses = self.model.rescale_to_sample(selections)
                for chemical, newmass in zip(self.model.chemicals, newmasses):
                    chemical.mass = newmass
                statictext.SetLabel("{0:6.2f}".format(self.model.sample_size))

    def SetResults(self):
        '''Set the OLV columns and put current Chemical objects in the OLV'''

        olv_cols = get_columns(["label", "mass", "volume"])
        self.resultOlv.SetColumns(olv_cols)
        self.resultOlv.SetObjects(self.model.chemicals)


class MolesOutputPanel(wx.Panel):

    def __init__(self, parent, session, model):
        super(MolesOutputPanel, self).__init__(parent, style=wx.SUNKEN_BORDER)

        self.model = model
        self.session = session

        resulttxt = wx.StaticText(self, -1, label="Results")
        resulttxt.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.resultOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER,
                                        useAlternateBackColors=True)
        self.resultOlv.evenRowsBackColor = "#DCF0C7"
        self.resultOlv.oddRowsBackColor = "#FFFFFF"
        calculatebtn = wx.Button(self, label="Calculate")
        rescalebtn = wx.Button(self, label="Rescale")

        self.SetResults()

        # Layout

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(resulttxt, 0, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5)
        vbox.Add(self.resultOlv, 1, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(calculatebtn, 0, flag=wx.ALL, border=5)
        hbox.Add(rescalebtn, 0, flag=wx.ALL, border=5)

        vbox.Add(hbox, 0, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT, border=10)

        self.SetSizer(vbox)
        self.Fit()

        # Event Handlers

        calculatebtn.Bind(wx.EVT_BUTTON, self.OnCalculateMoles)
        rescalebtn.Bind(wx.EVT_BUTTON, self.OnRescaleMoles)

    def OnCalculateMoles(self, event):
        '''
        Calculate the number moles of the batch components based on the masses
        of chemicals and display the result in the OLV.
        '''

        self.model.calculate_moles(self.session)
        self.resultOlv.SetObjects(self.model.components)

    def OnRescaleMoles(self, event):
        '''
        Retrieve the selected item and the amount of moles for that item to
        which it should be scaled, then rescale all the components and display
        them.
        '''

        rtsd = dialogs.RescaleToItemDialog(self, self.model.components,
                cols=get_columns(["label", "moles"]), title="Choose one component and enter moles")
        result = rtsd.ShowModal()
        if result == wx.ID_OK:
            amount, item = rtsd.GetCurrentSelections()
            try:
                amount = float(amount)
            except:
                amount = 1.0
                ed = wx.MessageDialog(None, "Amount must be a number",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()

            if len(item) == 0 or len(item) > 1:
                dlg = wx.MessageDialog(None, "Precisely one item has to be selected.",
                                       "", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                newmoles = self.model.rescale_to_item(item[0], amount)
                for c, m in zip(self.model.components, newmoles):
                    c.moles = m
                self.resultOlv.SetObjects(self.model.components)
                self.Layout()

    def SetResults(self):
        '''Set the OLV columns and put current Component objects in the OLV'''

        olv_cols = get_columns(["label", "moles", "mass"])
        self.resultOlv.SetColumns(olv_cols)
        self.resultOlv.SetObjects(self.model.components)


class InverseBatch(wx.Frame):

    def __init__(self, parent, title=""):
        super(InverseBatch, self).__init__(parent, id=-1, title="",
                                           pos=wx.DefaultPosition,
                                           size=(600, 600),
                                           style=wx.DEFAULT_FRAME_STYLE,
                                           name="")

        self.session = ctrl.get_session()
        self.model = BatchCalculator()

        panel = wx.Panel(self)
        self.inppanel = MolesInputPanel(panel, self.session, self.model)
        self.outpanel = MolesOutputPanel(panel, self.session, self.model)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.inppanel, 1, flag=wx.CENTER|wx.EXPAND)
        vbox.Add(self.outpanel, 1, flag=wx.CENTER|wx.EXPAND)

        panel.SetSizer(vbox)
        panel.Fit()

        # Menu

        menubar = wx.MenuBar()

        # File Menu
        filem = wx.Menu()
        mnew  = filem.Append(wx.ID_NEW, "&New\tCtrl+N", "New")
        filem.AppendSeparator()
        mepdf = filem.Append(wx.ID_ANY, "Export pdf")
        filem.AppendSeparator()
        mexit = filem.Append(wx.ID_CLOSE, "Exit\tAlt+F4")
        menubar.Append(filem, "&File")
        viewm = wx.Menu()
        mshowb = viewm.Append(wx.ID_ANY, "Show B Matrix")
        menubar.Append(viewm, "&View")
        self.SetMenuBar(menubar)
        # Database Menu
        dbm = wx.Menu()
        mchangedb = dbm.Append(wx.ID_ANY, "Change db\t", "Switch to a different database")
        menubar.Append(dbm, "Database")

        # Event Handlers

        # Bind Menu Handlers
        self.Bind(wx.EVT_MENU, self.OnNew, mnew)
        self.Bind(wx.EVT_MENU, self.OnExit, mexit)
        self.Bind(wx.EVT_MENU, self.OnExportPdf, mepdf)
        self.Bind(wx.EVT_MENU, self.OnShowB, mshowb)
        self.Bind(wx.EVT_MENU, self.OnChangeDB, mchangedb)

    # Menu Bindings ------------------------------------------------------------

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
            self.session = ctrl.get_session(path)
        dlg.Destroy()

    def OnExit(self, event):
        self.Close()

    def OnExportPdf(self, event):
        '''
        Open the dialog with options about the pdf document to be written.
        '''

        dlg = dialogs.ExportPdfMinimalDialog(parent=self, id=-1, size=(400, 330))
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            flags = dlg.get_data()
            path = self.OnSavePdf()
            try:
                create_pdf_composition(path, self.model, flags)
            except:
                dlg = wx.MessageDialog(None, "An error occured while generating pdf",
                                        "", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                raise
            else:
                dlg = wx.MessageDialog(None, "Successfully generated pdf",
                                        "", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

    def OnNew(self, event):
        self.model.reset()
        self.inppanel.SetComponents()
        self.inppanel.SetChemicals()
        self.outpanel.SetResults()

    def OnSavePdf(self):
        '''
        Open the file dialog to choose the name of the pdf file.
        '''

        pdfwildcard = "pdf Files (*.pdf)|*pdf|"     \
                      "All files (*.*)|*.*"


        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(),
            defaultFile="", wildcard=pdfwildcard, style=wx.SAVE|wx.OVERWRITE_PROMPT
            )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if not os.path.splitext(path)[1] == '.pdf':
                path += '.pdf'
            return path
        else:
            return

    def OnShowB(self, event):

        if isinstance(self.model.B, list):
            dlg = wx.MessageDialog(None, "Batch Matrix needs to be defined first.",
                                    "", wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        elif type(self.model.B).__module__ == np.__name__:
            frame = ShowBFrame(self, sys.stdout)
            frame.Show(True)


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

        self.gray = "#939393"

        # global dbpath
        self.session = ctrl.get_session()

        self.model = BatchCalculator()

        main_panel = wx.Panel(self)
        splitter = wx.SplitterWindow(main_panel)

        self.inppanel = InputPanel(splitter, self.session, self.model)
        self.outpanel = OutputPanel(splitter, self.session, self.model)

        splitter.SplitHorizontally(self.inppanel, self.outpanel)
        splitter.SetSashGravity(0.5)

        #self.inppanel = InputPanel(main_panel, self.model)
        #self.outpanel = OutputPanel(main_panel, self.model)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(splitter, 1, wx.EXPAND)
        #vbox.Add(self.inppanel, 1, flag=wx.CENTER|wx.EXPAND)
        #vbox.Add(self.outpanel, 1, flag=wx.CENTER|wx.EXPAND)
        main_panel.SetSizer(vbox)
        main_panel.Fit()

        # Menu

        menubar = wx.MenuBar()

        # File Menu
        filem = wx.Menu()
        mnew = filem.Append(wx.ID_NEW, "&New\tCtrl+N", "New")
        filem.AppendSeparator()
        mopen = filem.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Open")
        msave = filem.Append(wx.ID_SAVE, "&Save\tCtrl+S", "Save")
        filem.AppendSeparator()
        metex = filem.Append(wx.ID_ANY, "Export TeX\t", "Export to a TeX file")
        mepdf = filem.Append(wx.ID_ANY, "Export pdf\t", "Export to a pdf file")
        filem.AppendSeparator()
        mexit = filem.Append(wx.ID_CLOSE, "Exit\tAlt+F4")
        menubar.Append(filem, "&File")
        # View Menu
        viewm = wx.Menu()
        mshowb = viewm.Append(wx.ID_ANY, "Show B Matrix")
        menubar.Append(viewm, "&View")
        calcm = wx.Menu()
        minvcalc = calcm.Append(wx.ID_ANY, "Calculate composition", "CC")
        menubar.Append(calcm, "Calculation")
        # Database Menu
        dbm = wx.Menu()
        mnewdb = dbm.Append(wx.ID_ANY, "New db\t", "Create a new database")
        dbm.AppendSeparator()
        mchangedb = dbm.Append(wx.ID_ANY, "Change db\t", "Switch to a different database")
        dbm.AppendSeparator()
        maddchemicaldb = dbm.Append(wx.ID_ANY, "Edit Chemicals\t", "Edit chemicals records in the database")
        maddcomponentdb = dbm.Append(wx.ID_ANY, "Edit Components\t", "Edit zeolite component records in the database")
        maddbatchdb = dbm.Append(wx.ID_ANY, "Edit Batch\t", "Edit batch records in the database")
        maddreactiondb = dbm.Append(wx.ID_ANY, "Edit Reactions\t", "Edit reaction records in the database")
        maddcategorydb = dbm.Append(wx.ID_ANY, "Edit Categories\t", "Edit category records in the database")
        menubar.Append(dbm, "Database")
        # Synthesis Menu
        synthm = wx.Menu()
        synth_show = synthm.Append(wx.ID_ANY, "Show All\t", "Show all stored syntheses")
        synth_save = synthm.Append(wx.ID_ANY, "Add current\t", "Save current calculation internally")
        menubar.Append(synthm, "Syntheses")
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
        self.Bind(wx.EVT_MENU, self.OnInverseCalculation, minvcalc)
        self.Bind(wx.EVT_MENU, self.OnShowB, mshowb)
        self.Bind(wx.EVT_MENU, self.OnExportTex, metex)
        self.Bind(wx.EVT_MENU, self.OnExportPdf, mepdf)
        self.Bind(wx.EVT_MENU, self.OnChangeDB, mchangedb)
        self.Bind(wx.EVT_MENU, self.OnNewDB, mnewdb)
        self.Bind(wx.EVT_MENU, self.OnAddChemicalToDB, maddchemicaldb)
        self.Bind(wx.EVT_MENU, self.OnAddComponentToDB, maddcomponentdb)
        self.Bind(wx.EVT_MENU, self.OnAddBatchToDB, maddbatchdb)
        self.Bind(wx.EVT_MENU, self.OnAddReactionToDB, maddreactiondb)
        self.Bind(wx.EVT_MENU, self.OnAddCategoryToDB, maddcategorydb)
        self.Bind(wx.EVT_MENU, self.OnShowSyntheses, synth_show)
        self.Bind(wx.EVT_MENU, self.OnSaveCalculation, synth_save)
        self.Bind(wx.EVT_MENU, self.OnAbout, about)

    # Menu Bindings ------------------------------------------------------------

    def OnAbout(self, event):
        '''
        Show the about dialog
        '''

        info = wx.AboutDialogInfo()
        info.SetName("Zeolite Batch Calculator")
        info.SetVersion(__version__)
        info.SetCopyright("Copyright (C) Lukasz Mentel")
        info.SetDescription(wordwrap("A GUI script based on wxPython for " +\
            "calculating the correct amount of reagents (batch) for a  "   +\
            "particular zeolite composition given by the molar ratio "     +\
            "of its components.", 350, wx.ClientDC(self)))

        info.WebSite = ("https://github.com/lmmentel/batchcalculator", "ZBC Code Repository")
        info.Developers = ["Katarzyna Lukaszuk"]
        #info.License = wordwrap(__doc__, 600, wx.ClientDC(self))
        wx.AboutBox(info)

    def OnAddBatchToDB(self, event):
        '''
        Add a Chemical to the Database
        '''

        frame = AddModifyBatchTableFrame(parent=self, size=(800, 600))
        frame.Show(True)

    def OnAddCategoryToDB(self, event):
        '''
        Add a Category to the Database
        '''

        frame = AddModifyCategoryTableFrame(parent=self, size=(400, 400))
        frame.Show(True)

    def OnAddChemicalToDB(self, event):
        '''
        Add a Chemical to the Database
        '''

        frame = AddModifyChemicalTableFrame(parent=self, size=(1000, 600))
        frame.Show(True)

    def OnAddComponentToDB(self, event):
        '''
        Add a Zeolite Component to the Database
        '''

        frame = AddModifyComponentTableFrame(parent=self, size=(800, 600))
        frame.Show(True)

    def OnAddReactionToDB(self, event):
        '''
        Add a Reaction to the Database
        '''

        frame = AddModifyReactionTableFrame(parent=self, size=(600, 600))
        frame.Show(True)

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
            self.session = ctrl.get_session(path)
        dlg.Destroy()

    def OnExit(self, event):
        self.session.close()
        self.Close()

    def OnExportTex(self, event):
        '''
        Open the dialog with options about the TeX document to be written.
        '''
        # recalculate the masses since the scaling is done in the printing
        # functions
        self.model.calculate_masses(self.session)

        etexdialog = dialogs.ExportTexDialog(parent=self, id=-1)
        result = etexdialog.ShowModal()
        if result == wx.ID_OK:
            flags = etexdialog.get_data()
            # get the string with contents of the TeX report
            tex = get_report_as_string(flags, self.model)
            self.OnSaveTeX(tex, flags['typeset'], flags['pdflatex'])

    def OnExportPdf(self, event):
        '''
        Open the dialog with options about the pdf document to be written.
        '''

        # recalculate the masses since the scaling is done in the printing
        # functions
        self.model.calculate_masses(self.session)

        dlg = dialogs.ExportPdfDialog(parent=self, id=-1, size=(400, 520))
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            flags = dlg.get_data()
            path = self.OnSavePdf()
            try:
                create_pdf(path, self.session, self.model, flags)
            except:
                dlg = wx.MessageDialog(None, "An error occured while generating pdf",
                                        "", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                raise
            else:
                dlg = wx.MessageDialog(None, "Successfully generated pdf",
                                        "", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

    def OnInverseCalculation(self, event):

        window = InverseBatch(self)
        window.Show()

    def OnNew(self, event):
        '''
        Start a new document by clearing all the lists
        '''

        # check if there is some results that might need saving
        if any(len(x) != 0 for x in [self.model.components,
                                     self.model.chemicals]):
            dlg = wx.MessageDialog(self, 'There are unsaved changes, Save now?',
                                'Save',
                                wx.YES_NO | wx.CANCEL | wx.ICON_WARNING
                                )
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                self.OnSave(-1)
                self.model.reset()
                self.update_all_objectlistviews()
            elif result == wx.ID_NO:
                self.model.reset()
                self.update_all_objectlistviews()
            else:
                event.Skip()

            dlg.Destroy()

    def OnNewDB(self, event):

        dbwildcard = "db Files (*.db)|*.db|"     \
                     "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message="Choose database file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=dbwildcard,
            style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR
            )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if os.path.exists(path):
                os.remove(path)
            self.session = ctrl.new_db(path)
            # fill the tables
            ctrl.fill_kinds_table(self.session)
            ctrl.fill_physical_forms_table(self.session)
            ctrl.fill_electrolytes_table(self.session)
            dlg = wx.MessageDialog(None, "Successfully created new database",
                                    "", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

        dlg.Destroy()

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
            (self.model.components, self.model.chemicals,\
            self.model.A, self.model.B, self.model.X,\
            self.model.scale_all, self.model.sample_scale,\
            self.model.sample_size, self.model.selections) = pickle.load(fp)

            fp.close()

            self.update_all_objectlistviews()

        dlg.Destroy()

    def OnSave(self, event):
        '''
        Open the save file dialog and save the model data to a file as a pickle.
        '''

        wildcard = "ZBC Files (*.zbc)|*.zbc|"     \
                   "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(),
            defaultFile="", wildcard=wildcard,
            style=wx.SAVE | wx.OVERWRITE_PROMPT)

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
                    self.model.chemicals,
                    self.model.A, self.model.B, self.model.X,
                    self.model.scale_all, self.model.sample_scale,
                    self.model.sample_size, self.model.selections)
            fp = file(path, 'wb')  # Create file anew
            pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)
            fp.close()

        dlg.Destroy()

    def OnSaveCalculation(self, event):
        '''
        Display the dialog to save the current calculation internally.
        '''

        # check if any calculation was done or if there are some chemicals and
        # components selected

        dlg = ctrl.AddModifySynthesisRecordDialog(parent=self,
                                                  model=self.model,
                                                  session=self.session,
                                                  record=None,
                                                  title="Add",
                                                  add_record=True)
        dlg.ShowModal()
        dlg.Destroy()

    def OnSavePdf(self):
        '''
        Open the file dialog to choose the name of the pdf file.
        '''

        pdfwildcard = "pdf Files (*.pdf)|*pdf|"     \
                      "All files (*.*)|*.*"

        dlg = wx.FileDialog(self, message="Save file as ...",
                            defaultDir=os.getcwd(), defaultFile="",
                            wildcard=pdfwildcard,
                            style=wx.SAVE | wx.OVERWRITE_PROMPT)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if not os.path.splitext(path)[1] == '.pdf':
                path += '.pdf'
            return path
        else:
            return

    def OnSaveTeX(self, texdata, typeset, pdflatex):

        texwildcard = "TeX Files (*.tex)|*tex|"     \
                      "All files (*.*)|*.*"

        opts = "-halt-on-error"

        dlg = wx.FileDialog(self, message="Save file as ...",
                            defaultDir=os.getcwd(), defaultFile="",
                            wildcard=texwildcard,
                            style=wx.SAVE | wx.OVERWRITE_PROMPT)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if not os.path.splitext(path)[1] == '.tex':
                path += '.tex'

            fp = file(path, 'w')  # Create file anew
            fp.write(texdata)
            fp.close()

            if typeset:
                if pdflatex is not None:
                    os.chdir(os.path.split(path)[0])
                    retcode = subprocess.call([pdflatex, opts, path], )
                    if retcode != 0:
                        dlg = wx.MessageDialog(None, "There were problems generating the pdf, check the log file {l:s}, return code: {r:d}".format(l=path.replace(".tex", ".log"), r=retcode),
                                                "", wx.OK | wx.ICON_WARNING)
                        dlg.ShowModal()
                        dlg.Destroy()
                    else:
                        # run again and clean the auxiliary files
                        retcode = subprocess.call([pdflatex, opts, path])
                        clean_tex(path)
                        dlg = wx.MessageDialog(None, "Successfully generated the pdf",
                                                "", wx.OK | wx.ICON_INFORMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                else:
                    dlg = wx.MessageDialog(None, "pdflatex not found, pdf not generated",
                                            "", wx.OK | wx.ICON_WARNING)
                    dlg.ShowModal()
                    dlg.Destroy()

    def OnShowB(self, event):

        if isinstance(self.model.B, list):
            dlg = wx.MessageDialog(None, "Batch Matrix needs to be defined first.",
                                    "", wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        elif type(self.model.B).__module__ == np.__name__:
            frame = ShowBFrame(self, sys.stdout)
            frame.Show(True)

    def OnShowSyntheses(self, event):
        '''Show a frame with all stored syntheses'''

        frame = ShowSynthesesFrame(parent=self, size=(1000, 600),
                                   session=self.session)
        frame.Show(True)

    def update_all_objectlistviews(self):
        '''
        Update all the ObjectListView with the current state of the model.
        '''

        self.inppanel.comp_olv.SetObjects(self.model.components)
        self.inppanel.chem_olv.SetObjects(self.model.chemicals)
        self.outpanel.resultOlv.SetObjects(self.model.chemicals)


def ExceptionHook(exctype, value, trace):
    '''
    Handler for all unhandled exceptions

    Args:
        exctype: Exception Type
        value:   Error Value
        trace:   Trace back info
    '''

    frame = wx.GetApp().GetTopWindow()
    # Format the traceback
    exc = traceback.format_exception(exctype, value, trace)
    ftrace = "".join(exc)
    app = wx.GetApp()
    msg = "An unexpected error has occurred: %s" % ftrace
    dlg = dialogs.ExceptionDialog(msg)
    dlg.ShowModal()
    dlg.Destroy()


class ZeoGui(wx.App):

    def OnInit(self):

        self.frame = MainFrame(None, title="Zeolite Batch Calculator",
                               size=(860, 600))
        # change the default exception handling
        sys.excepthook = ExceptionHook
        self.SetTopWindow(self.frame)
        self.frame.Show()

        return True


def main():

    app = ZeoGui(False)
    # uncomment for debugging
    # import wx.lib.inspection
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
