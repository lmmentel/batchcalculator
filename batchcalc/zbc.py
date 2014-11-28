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

__version__ = "0.1.2"

import copy
import os
import pickle
import subprocess
import sys
import traceback
from collections import OrderedDict

import numpy as np

import wx
import wx.grid as gridlib
from wx.lib.wordwrap import wordwrap
# ObjectListView
from ObjectListView import ObjectListView, ColumnDefn

from batchcalc.tex_writer import get_report_as_string
from batchcalc.calculator import BatchCalculator
from batchcalc import dialogs, controller

# uncomment for debugging
#import wx.lib.inspection

def clean_tex(fname):
    '''
    Clean the auxiliary tex files.
    '''
    exts = [".out", ".aux", ".log", ".tex"]
    fbase = os.path.splitext(fname)[0]
    for fil in [fbase + ext for ext in exts]:
        if os.path.exists(fil):
            os.remove(fil)

def format_float(item):

    if item is not None:
        return "{0:7.3f}".format(item)
    else:
        return ""

class AddModifyDBBaseFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="Edit Database",
            pos=wx.DefaultPosition, size=(500, 300),
            style=wx.DEFAULT_FRAME_STYLE, name=""):

        super(AddModifyDBBaseFrame, self).__init__(parent, id, title, pos, size, style, name)

        panel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)

        self.olv = ObjectListView(self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.olv.evenRowsBackColor="#DCF0C7"
        self.olv.oddRowsBackColor="#FFFFFF"
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

        mainSizer.Add(self.olv, 1, wx.ALL|wx.EXPAND, 5)
        mainSizer.Add(btnSizer, 0, wx.CENTER)
        self.SetSizer(mainSizer)

    def onAddRecord(self, event):
        """
        Add a record to the database
        """
        print "adding"

    def onEditRecord(self, event):
        """
        Edit a record
        """
        print "editing"

    def onDelete(self, event):
        """
        Delete a record
        """
        print "deleting"

    def onSearch(self, event):
        """
        Searches database based on the user's filter choice and keyword
        """
        print "searching"

    def onShowAllRecords(self, event):
        """
        Updates the record list to show all of them
        """
        print "showing all"

class AddModifyBatchTableFrame(AddModifyDBBaseFrame):

    def __init__(self, parent, **kwargs):

        super(AddModifyBatchTableFrame, self).__init__(parent, **kwargs)
        self.model = parent.model

        self.show_all()

    def onAddRecord(self, event):
        """
        Add a record to the database
        """
        print "adding batch record"
        dlg = controller.AddModifyBatchRecordDialog(self,
                                                    session=self.model.session,
                                                    title="Add",
                                                    add_record=True)
        dlg.ShowModal()
        dlg.Destroy()
        self.show_all()

    def onEditRecord(self, event):
        """
        Edit a record
        """
        print "editing batch record"
        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        print sel_row
        dlg = controller.AddModifyBatchRecordDialog(self,
                                                    session=self.model.session,
                                                    record=sel_row,
                                                    title="Modify",
                                                    add_record=False)
        result = dlg.ShowModal()
        if result == wx.ID_SAVE:
            print "saving batch result"
            print dlg.get_data()
        dlg.Destroy()
        self.show_all()

    def onDelete(self, event):
        """
        Delete a record
        """
        print "deleting batch reord"
        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        print sel_row
        controller.delete_batch_record(self.model.session, sel_row.id)
        self.show_all()

    def onSearch(self, event):
        """
        Searches database based on the user's filter choice and keyword
        """
        print "searching chemical"

    def onShowAllRecords(self, event):
        """
        Updates the record list to show all of them
        """
        self.show_all()

    def set_olv(self, batches):

        self.olv.SetColumns([
            ColumnDefn(title="Id",          minimumWidth=50,  width=50,  align="left",  valueGetter="id", isEditable=False),
            ColumnDefn(title="Chemical",    minimumWidth=150, width=200, align="left",  valueGetter="chemical", isEditable=False, isSpaceFilling=True),
            ColumnDefn(title="Component",   minimumWidth=150, width=200, align="left",  valueGetter="component", isEditable=False, isSpaceFilling=True),
            ColumnDefn(title="Coefficient", minimumWidth=100, width=100, align="right", valueGetter="coefficient", isEditable=False, stringConverter="%.2f"),
            ColumnDefn(title="Reaction",    minimumWidth=200, width=200, align="left",  valueGetter="reaction", isEditable=False, isSpaceFilling=True),
        ])
        self.olv.SetObjects(batches)

    def show_all(self):

        batches = self.model.get_batch_records()
        self.set_olv(batches)

class AddModifyChemicalTableFrame(AddModifyDBBaseFrame):

    def __init__(self, parent, **kwargs):

        super(AddModifyChemicalTableFrame, self).__init__(parent, **kwargs)
        self.model = parent.model

        self.show_all()

    def onAddRecord(self, event):
        """
        Add a record to the database
        """
        print "adding chemical"
        dlg = controller.AddModifyChemicalRecordDialog(self,
                                                    session=self.model.session,
                                                    title="Add",
                                                    add_record=True)
        dlg.ShowModal()
        dlg.Destroy()
        self.show_all()

    def onEditRecord(self, event):
        """
        Edit a record
        """
        print "editing chemical"
        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        print sel_row
        dlg = controller.AddModifyChemicalRecordDialog(self,
                                                    session=self.model.session,
                                                    record=sel_row,
                                                    title="Modify",
                                                    add_record=False)
        result = dlg.ShowModal()
        if result == wx.ID_SAVE:
            print "saving result"
            print dlg.get_data()
        dlg.Destroy()
        self.show_all()

    def onDelete(self, event):
        """
        Delete a record
        """
        print "deleting chemical"
        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        print sel_row
        controller.delete_chemical_record(self.model.session, sel_row.id)
        self.show_all()

    def onSearch(self, event):
        """
        Searches database based on the user's filter choice and keyword
        """
        print "searching chemical"

    def onShowAllRecords(self, event):
        """
        Updates the record list to show all of them
        """
        self.show_all()

    def set_olv(self, chemicals):

        self.olv.SetColumns([
            ColumnDefn(title="Id",               minimumWidth=50,  width=50,  align="left",  valueGetter="id", isEditable=False),
            ColumnDefn(title="Name",             minimumWidth=200, width=200, align="left",  valueGetter="name", isEditable=False, isSpaceFilling=True),
            ColumnDefn(title="Formula",          minimumWidth=120, width=120, align="left",  valueGetter="formula", isEditable=False, isSpaceFilling=True),
            ColumnDefn(title="Concentration",    minimumWidth=100, width=100, align="right", valueGetter="concentration", isEditable=False, stringConverter="%.2f"),
            ColumnDefn(title="Molecular Weight", minimumWidth=120, width=120, align="right", valueGetter="molwt", isEditable=False, stringConverter="%.4f"),
            ColumnDefn(title="Short name",       minimumWidth=120, width=120, align="left",  valueGetter="short_name", isEditable=False),
            ColumnDefn(title="Kind",             minimumWidth=120, width=120, align="left",  valueGetter="kind", isEditable=False),
            ColumnDefn(title="Physical Form",    minimumWidth=120, width=120, align="left",  valueGetter="physical_form", isEditable=False),
            ColumnDefn(title="Electrolyte",      minimumWidth=120, width=120, align="left",  valueGetter="electrolyte", isEditable=False),
            ColumnDefn(title="CAS No.",          minimumWidth=120, width=120, align="left",  valueGetter="cas", isEditable=False),
            ColumnDefn(title="pK",               minimumWidth=120, width=120, align="right", valueGetter="pk", isEditable=False, stringConverter=format_float),
            ColumnDefn(title="Density",          minimumWidth=120, width=120, align="right", valueGetter="density", isEditable=False, stringConverter=format_float),
            ColumnDefn(title="SMILES",           minimumWidth=150, width=120, align="left",  valueGetter="smiles", isEditable=False),
        ])
        self.olv.SetObjects(chemicals)

    def show_all(self):

        chemicals = self.model.get_chemicals(showall=True)
        self.set_olv(chemicals)

class AddModifyComponentTableFrame(AddModifyDBBaseFrame):

    def __init__(self, parent, **kwargs):

        super(AddModifyComponentTableFrame, self).__init__(parent, **kwargs)
        self.model = parent.model

        self.show_all()

    def onAddRecord(self, event):
        """
        Add a record to the database
        """
        print "adding component"
        dlg = controller.AddModifyComponentRecordDialog(self,
                                                        session=self.model.session,
                                                        title="Add",
                                                        add_record=True)
        dlg.ShowModal()
        dlg.Destroy()
        self.show_all()

    def onEditRecord(self, event):
        """
        Edit a record
        """
        print "editing component"
        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        print sel_row
        dlg = controller.AddModifyComponentRecordDialog(self,
                                                        session=self.model.session,
                                                        record=sel_row,
                                                        title="Modify",
                                                        add_record=False)
        result = dlg.ShowModal()
        if result == wx.ID_SAVE:
            print "saving result"
            print dlg.get_data()
        dlg.Destroy()
        self.show_all()

    def onDelete(self, event):
        """
        Delete a record
        """
        print "deleting component"
        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        print sel_row
        controller.delete_component_record(self.model.session, sel_row.id)
        self.show_all()

    def onSearch(self, event):
        """
        Searches database based on the user's filter choice and keyword
        """
        print "searching chemical"

    def onShowAllRecords(self, event):
        """
        Updates the record list to show all of them
        """
        self.show_all()

    def set_olv(self, components):

        self.olv.SetColumns([
            ColumnDefn(title="Id",               minimumWidth=50,  width=50,  align="left",  valueGetter="id", isEditable=False),
            ColumnDefn(title="Name",             minimumWidth=200, width=200, align="left",  valueGetter="name", isEditable=False, isSpaceFilling=True),
            ColumnDefn(title="Formula",          minimumWidth=120, width=120, align="left",  valueGetter="formula", isEditable=False, isSpaceFilling=True),
            ColumnDefn(title="Molecular Weight", minimumWidth=120, width=120, align="right", valueGetter="molwt", isEditable=False, stringConverter="%.4f"),
            ColumnDefn(title="Short name",       minimumWidth=120, width=120, align="left",  valueGetter="short_name", isEditable=False),
            ColumnDefn(title="Category",         minimumWidth=120, width=120, align="left",  valueGetter="category", isEditable=False),
        ])
        self.olv.SetObjects(components)

    def show_all(self):

        components = self.model.get_components()
        self.set_olv(components)

class AddModifyCategoryTableFrame(AddModifyDBBaseFrame):

    def __init__(self, parent, **kwargs):

        super(AddModifyCategoryTableFrame, self).__init__(parent, **kwargs)
        self.model = parent.model

        self.show_all()

    def onAddRecord(self, event):
        """
        Add a record to the database
        """

        dlg = wx.TextEntryDialog(None,
            "Enter new category",
            "Enter new category", "", style=wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            category = dlg.GetValue()
            if category != "":
                controller.add_category_record(self.model.session, category)
            else:
                ed = wx.MessageDialog(None, "Nothing entered",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()
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
        print sel_row

        dlg = wx.TextEntryDialog(None,
            "Enter the category",
            "Enter the category", sel_row.name, style=wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            category = dlg.GetValue()
            if category != "":
                controller.modify_category_record(self.model.session, sel_row.id, category)
            else:
                ed = wx.MessageDialog(None, "Nothing entered",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()
        dlg.Destroy()
        self.show_all()

    def onDelete(self, event):
        """
        Delete a record
        """
        print "deleting reaction record"
        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        print sel_row
        controller.delete_category_record(self.model.session, sel_row.id)
        self.show_all()

    def onShowAllRecords(self, event):
        """
        Updates the record list to show all of them
        """
        self.show_all()

    def set_olv(self, categories):

        self.olv.SetColumns([
            ColumnDefn(title="Id",          minimumWidth=50,  width=50,  align="left",  valueGetter="id", isEditable=False),
            ColumnDefn(title="Category",    minimumWidth=150, width=200, align="left",  valueGetter="name", isEditable=False, isSpaceFilling=True),
        ])
        self.olv.SetObjects(categories)

    def show_all(self):

        categories = self.model.get_categories()
        self.set_olv(categories)

class AddModifyReactionTableFrame(AddModifyDBBaseFrame):

    def __init__(self, parent, **kwargs):

        super(AddModifyReactionTableFrame, self).__init__(parent, **kwargs)
        self.model = parent.model

        self.show_all()

    def onAddRecord(self, event):
        """
        Add a record to the database
        """
        print "adding reaction record"
        dlg = wx.TextEntryDialog(None,
            "Enter the reaction",
            "Enter the reaction", "", style=wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            reaction = dlg.GetValue()
            if reaction != "":
                controller.add_reaction_record(self.model.session, reaction)
            else:
                ed = wx.MessageDialog(None, "Nothing entered",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()
        dlg.Destroy()
        self.show_all()

    def onEditRecord(self, event):
        """
        Edit a record
        """
        print "editing reaction record"
        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        print sel_row

        dlg = wx.TextEntryDialog(None,
            "Enter the reaction",
            "Enter the reaction", sel_row.reaction, style=wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            reaction = dlg.GetValue()
            if reaction != "":
                controller.modify_reaction_record(self.model.session, sel_row.id, reaction)
            else:
                ed = wx.MessageDialog(None, "Nothing entered",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()
        dlg.Destroy()
        self.show_all()

    def onDelete(self, event):
        """
        Delete a record
        """
        print "deleting reaction record"
        sel_row = self.olv.GetSelectedObject()
        if sel_row is None:
            dialogs.show_message_dlg("No row selected", "Error")
            return
        print sel_row
        controller.delete_reaction_record(self.model.session, sel_row.id)
        self.show_all()

    def onSearch(self, event):
        """
        Searches database based on the user's filter choice and keyword
        """
        print "searching chemical"

    def onShowAllRecords(self, event):
        """
        Updates the record list to show all of them
        """
        self.show_all()

    def set_olv(self, reactions):

        self.olv.SetColumns([
            ColumnDefn(title="Id",          minimumWidth=50,  width=50,  align="left",  valueGetter="id", isEditable=False),
            ColumnDefn(title="Reaction",    minimumWidth=250, width=300, align="left",  valueGetter="reaction", isEditable=False, isSpaceFilling=True),
        ])
        self.olv.SetObjects(reactions)

    def show_all(self):

        reactions = self.model.get_reactions()
        self.set_olv(reactions)

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
        self.row_labels = [x.listctrl_label() for x in model.chemicals]

        self.data_types = [gridlib.GRID_VALUE_FLOAT]*len(model.chemicals)

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
        self.SetRowLabelSize(200)

        gridlib.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)


    # I do this because I don't like the default behaviour of not starting the
    # cell editor on double clicks, but only a second click.
    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

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

    def __init__(self, parent, model, columns):
        super(InputPanel, self).__init__(parent, style=wx.SUNKEN_BORDER)

        # Attributes

        self.model = model
        self.columns = columns

        cmptxt = wx.StaticText(self, -1, label="Components")
        rcttxt = wx.StaticText(self, -1, label="Chemicals")
        cmptxt.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        rcttxt.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.compOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.compOlv.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
        self.compOlv.rowFormatter = compRowFormatter


        self.reacOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER,
                useAlternateBackColors=True)
        self.reacOlv.evenRowsBackColor="#DCF0C7"
        self.reacOlv.oddRowsBackColor="#FFFFFF"
        self.reacOlv.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK

        self.SetComponents()
        self.SetChemicals()
        zeobtn = wx.Button(self, -1, label="Add/Remove")
        rctbtn = wx.Button(self, -1, label="Add/Remove")

        # Layout

        #fgs = wx.FlexGridSizer(rows=3, cols=2, hgap=10, vgap=10)
        gbs = wx.GridBagSizer(hgap=10, vgap=10)

        gbs.Add(cmptxt, pos=(0,0), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border=5)
        gbs.Add(rcttxt, pos=(0,1), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border=5)

        gbs.Add(self.compOlv, pos=(1, 0), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.GROW|wx.LEFT, border=10)
        gbs.Add(self.reacOlv, pos=(1, 1), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.GROW|wx.RIGHT, border=10)

        gbs.Add(zeobtn, pos=(2, 0), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, border=5)
        gbs.Add(rctbtn, pos=(2, 1), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, border=5)

        gbs.AddGrowableCol(0)
        gbs.AddGrowableCol(1)
        gbs.AddGrowableRow(1)

        self.SetSizer(gbs)
        self.Fit()

        # Event Handlers

        zeobtn.Bind(wx.EVT_BUTTON, self.OnAddRemoveComponents)
        rctbtn.Bind(wx.EVT_BUTTON, self.OnAddRemoveChemicals)

    def get_component_cols(self):
        fields = ["name", "formula", "molwt", "short", "category"]
        return [self.columns[k] for k in fields]

    def get_chemicals_cols(self):
        fields = ["name", "formula", "conc", "molwt", "short", "kind", "physform", "cas"]
        return [self.columns[k] for k in fields]

    def OnAddRemoveComponents(self, event):
        '''
        Show the dialog with the zeolite components retrieved from the
        database.
        '''

        self.dlg = dialogs.ComponentsDialog(self, self.model, self.get_component_cols(),
                                   id=-1, title="Choose Zeolite Components...")
        result = self.dlg.ShowModal()
        if result == wx.ID_OK:
            self.model.components = self.dlg.GetCurrentSelections()
        self.compOlv.SetObjects(self.model.components)
        self.dlg.Destroy()

    def OnAddRemoveChemicals(self, event):
        '''
        Show the dialog with the chemicals retrieved from the database.
        '''

        self.dlg = dialogs.ChemicalsDialog(self, self.model, self.get_chemicals_cols(),
                                  id=-1, title="Choose Chemicals...")
        result = self.dlg.ShowModal()
        if result == wx.ID_OK:
            self.model.chemicals = self.dlg.GetCurrentSelections()
        self.reacOlv.SetObjects(self.model.chemicals)
        self.dlg.Destroy()

    def SetComponents(self, columns=None):

        self.compOlv.SetColumns([
            ColumnDefn("Label", "left", 100, "listctrl_label", isEditable=False, isSpaceFilling=True),
            ColumnDefn("Moles", "right", 100, "moles", isEditable=True, stringConverter="%.4f"),
        ])
        self.compOlv.SetObjects(self.model.components)

    def SetChemicals(self, columns=None):

        self.reacOlv.SetColumns([
            ColumnDefn("Label", "left", 100, "listctrl_label", isEditable=False, isSpaceFilling=True),
            ColumnDefn("Concentration", "right", 100, "concentration", isEditable=True, stringConverter="%.3f"),
        ])
        self.reacOlv.SetObjects(self.model.chemicals)

class MolesInputPanel(InputPanel):

    def __init__(self, parent, model, columns):
        super(MolesInputPanel, self).__init__(parent, model, columns)

    def SetComponents(self):

        self.compOlv.SetColumns([
            ColumnDefn("Label", "left", 150, "listctrl_label", isEditable=False, isSpaceFilling=True),
        ])
        self.compOlv.SetObjects(self.model.components)

    def SetChemicals(self):

        self.reacOlv.SetColumns([
            ColumnDefn("Label", "left", 100, "listctrl_label", isEditable=False, isSpaceFilling=True),
            ColumnDefn("Mass", "right", 150, "mass", isEditable=True, stringConverter="%.4f"),
            ColumnDefn("Concentration", "right", 100, "concentration", isEditable=True, stringConverter="%.2f"),
        ])
        self.reacOlv.SetObjects(self.model.chemicals)

class OutputPanel(wx.Panel):

    def __init__(self, parent, model, columns):
        super(OutputPanel, self).__init__(parent, style=wx.SUNKEN_BORDER)

        self.model = model
        self.columns = columns

        # Attributes

        self.gray   = "#939393"

        resulttxt = wx.StaticText(self, -1, label="Results [X]")
        resulttxt.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.rescaledtxt = wx.StaticText(self, -1, label="Rescaled")
        self.rescaledtxt.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.resultOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER,
                useAlternateBackColors=True)
        self.resultOlv.evenRowsBackColor="#DCF0C7"
        self.resultOlv.oddRowsBackColor="#FFFFFF"
        self.scaledOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER,
                useAlternateBackColors=True)
        self.resultOlv.evenRowsBackColor="#DCF0C7"
        self.resultOlv.oddRowsBackColor="#FFFFFF"

        calculateBtn = wx.Button(self, label="Calculate")
        rescaleAllBtn = wx.Button(self, label="Rescale All")
        rescaleToSampleBtn = wx.Button(self, label="Rescale To Sample")
        rescaleToItemBtn = wx.Button(self, label="Rescale To Item")

        self.SetResults()
        self.SetScaled()

        # Layout

        fgs = wx.FlexGridSizer(rows=3, cols=2, hgap=10, vgap=10)

        fgs.AddGrowableCol(0)
        fgs.AddGrowableCol(1)
        fgs.AddGrowableRow(1)

        fgs.Add(resulttxt, 0, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.TOP, border=5)
        fgs.Add(self.rescaledtxt, 0, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, border=5)

        fgs.Add(self.resultOlv, 0, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.GROW|wx.LEFT, border=10)
        fgs.Add(self.scaledOlv, 0, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.GROW|wx.RIGHT, border=10)

        fgs.Add(calculateBtn, 0, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT, border=10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(rescaleAllBtn, 0, flag=wx.LEFT|wx.RIGHT, border=5)
        hbox.Add(rescaleToSampleBtn, 0, flag=wx.LEFT|wx.RIGHT, border=5)
        hbox.Add(rescaleToItemBtn, 0, flag=wx.LEFT|wx.RIGHT, border=5)
        fgs.Add(hbox, 0, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, border=10)

        self.SetSizer(fgs)
        self.Fit()

        # Event Handlers

        calculateBtn.Bind(wx.EVT_BUTTON, self.OnCalculate)
        rescaleAllBtn.Bind(wx.EVT_BUTTON, self.OnRescaleAll)
        rescaleToSampleBtn.Bind(wx.EVT_BUTTON, self.OnRescaleToSample)
        rescaleToItemBtn.Bind(wx.EVT_BUTTON, self.OnRescaleToItem)

    def get_rescale_columns(self):
        fields = ["label", "mass"]
        return [self.columns[k] for k in self.columns.keys() if k in fields]

    def OnCalculate(self, event):

        self.model.calculate()
        self.resultOlv.SetObjects(self.model.chemicals)

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
                self.RescaleAll()
                self.Layout()
            except:
                ed = wx.MessageDialog(None, "Scale factor must be a number",
                                      "", wx.OK | wx.ICON_INFORMATION)
                ed.ShowModal()
                ed.Destroy()
        dialog.Destroy()

    def get_rescale_columns(self):
        fields = ["label", "mass"]
        return [self.columns[k] for k in self.columns.keys() if k in fields]

    def OnRescaleToItem(self, event):
        '''
        Retrieve the selected item and the mass for that item to which it
        should be scaled, then rescale all the components and display them.
        '''

        rtsd = dialogs.RescaleToItemDialog(self, self.model.chemicals, self.get_rescale_columns(), title="Choose chemical and desired mass")
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
                chemicals = copy.deepcopy(self.model.chemicals)
                newmasses = self.model.rescale_to_chemical(item[0], mass)
                for c, m  in zip(chemicals, newmasses):
                    c.mass = m
                self.scaledOlv.SetObjects(chemicals)
                self.rescaledtxt.SetLabel("Rescaled to {0:6.2f}g of {1:s}".format(mass, item[0].formula))
                self.Layout()

    def OnRescaleToSample(self, event):
        '''
        Retrieve the scaling factor and selections from a custom dialog, then
        calculate the scaling factor so that the selected item after rescaling
        sum up to the sample size. Use the scaling factor to rescale all the
        items and print them to the ListCtrl.
        '''

        rto = dialogs.RescaleToSampleDialog(self, self.model, self.get_rescale_columns(), title="Choose chemicals and sample size")
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
                chemicals = copy.deepcopy(self.model.chemicals)
                newmasses = self.model.rescale_to_sample(selections)
                for reac, newmass in zip(chemicals, newmasses):
                    reac.mass = newmass
                self.scaledOlv.SetObjects(chemicals)
                self.rescaledtxt.SetLabel("Rescaled to {0:8.3f} [g]".format(self.model.sample_size))
                self.Layout()

    def RescaleAll(self):

        chemicals = copy.deepcopy(self.model.chemicals)
        newmasses = self.model.rescale_all()
        for chemical, newmass in zip(chemicals, newmasses):
            chemical.mass = newmass
        self.scaledOlv.SetObjects(chemicals)
        self.rescaledtxt.SetLabel("Rescaled by {0:8.3f}".format(self.model.scale_all))

    def SetResults(self):

        self.resultOlv.SetColumns([
            ColumnDefn("Label", "left", 100, "listctrl_label", isEditable=False, isSpaceFilling=True),
            ColumnDefn("Mass [g]", "right", 120, "mass", isEditable=False, stringConverter="%.4f"),
            ColumnDefn("Volume [cm3]", "right", 120, "volume", isEditable=False, stringConverter=format_float),
        ])
        self.resultOlv.SetObjects(self.model.chemicals)

    def SetScaled(self):

        self.scaledOlv.SetColumns([
            ColumnDefn("Label", "left", 100, "listctrl_label", isEditable=False, isSpaceFilling=True),
            ColumnDefn("Scaled Mass [g]", "right", 120, "mass", isEditable=False, stringConverter="%.4f"),
            ColumnDefn("Volume [cm3]", "right", 120, "volume", isEditable=False, stringConverter=format_float),
        ])
        self.scaledOlv.SetObjects(self.model.chemicals)

class MolesOutputPanel(wx.Panel):

    def __init__(self, parent, model, columns):
        super(MolesOutputPanel, self).__init__(parent, style=wx.SUNKEN_BORDER)

        self.model = model
        self.columns = columns

        resulttxt = wx.StaticText(self, -1, label="Results")
        resulttxt.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.resultOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER,
                useAlternateBackColors=True)
        self.resultOlv.evenRowsBackColor="#DCF0C7"
        self.resultOlv.oddRowsBackColor="#FFFFFF"
        calculatebtn = wx.Button(self, label="Calculate")
        rescalebtn = wx.Button(self, label="Rescale All")

        self.SetResults()

        # Layout

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(resulttxt, 0, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=5)
        vbox.Add(self.resultOlv, 1, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(calculatebtn, 0, flag=wx.ALL, border=5)
        hbox.Add(rescalebtn, 0, flag=wx.ALL, border=5)

        vbox.Add(hbox, 0, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.RIGHT, border=10)

        self.SetSizer(vbox)
        self.Fit()

        # Event Handlers

        calculatebtn.Bind(wx.EVT_BUTTON, self.OnCalculateMoles)
        rescalebtn.Bind(wx.EVT_BUTTON, self.OnRescaleMoles)

    def get_rescale_columns(self):
        fields = ["label", "moles"]
        return [self.columns[k] for k in self.columns.keys() if k in fields]

    def OnCalculateMoles(self, event):

        self.model.calculate_moles()
        self.resultOlv.SetObjects(self.model.components)

    def OnRescaleMoles(self, event):
        '''
        Retrieve the selected item and the amount of moles for that item to
        which it should be scaled, then rescale all the components and display
        them.
        '''

        rtsd = dialogs.RescaleToItemDialog(self, self.model.components, self.get_rescale_columns(), title="Choose chemical and desired mass")
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
                for c, m  in zip(self.model.components, newmoles):
                    c.moles = m
                self.resultOlv.SetObjects(self.model.components)
                self.Layout()

    def SetResults(self):

        self.resultOlv.SetColumns([
            ColumnDefn("Label", "left", 100, "listctrl_label", isEditable=False, isSpaceFilling=True),
            ColumnDefn("Moles", "right", 150, "moles", isEditable=False, stringConverter="%.4f"),
            ColumnDefn("Mass", "right", 150, "mass", isEditable=False, stringConverter="%.4f"),
        ])
        self.resultOlv.SetObjects(self.model.components)

class InverseBatch(wx.Frame):

    def __init__(self, parent, title=""):
        super(InverseBatch, self).__init__(parent, id=-1, title="",
                                           pos=wx.DefaultPosition,
                                           size=(600, 600),
                                           style=wx.DEFAULT_FRAME_STYLE,
                                           name="")
        self.model = BatchCalculator()
        panel = wx.Panel(self)
        self.inppanel = MolesInputPanel(panel, self.model, parent.columns)
        self.outpanel = MolesOutputPanel(panel, self.model, parent.columns)
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
            self.model.new_dbsession(path)
        dlg.Destroy()

    def OnExit(self, event):
        self.Close()

    def OnNew(self, event):
        self.model.reset()
        self.inppanel.SetComponents()
        self.inppanel.SetChemicals()
        self.outpanel.SetResults()

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

        self.columns = OrderedDict([
            ("cas"     , {"title" : "CAS No.",          "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "cas", "isEditable" : False}),
            ("category", {"title" : "Category",         "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "category", "isEditable" : False}),
            ("conc"    , {"title" : "Concentration",    "minimumWidth" : 100, "width" : 100, "align" : "right", "valueGetter" : "concentration", "isEditable" : True, "stringConverter" : "%.2f"}),
            ("density" , {"title" : "Density",          "minimumWidth" : 120, "width" : 120, "align" : "right", "valueGetter" : "density", "isEditable" : False, "stringConverter" : "%.4f"}),
            ("elect"   , {"title" : "Electrolyte",      "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "electrolyte", "isEditable" : False, "isSpaceFilling" : True}),
            ("formula" , {"title" : "Formula",          "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "formula", "isEditable" : False, "isSpaceFilling" : True}),
            ("id"      , {"title" : "Id",               "minimumWidth" : 50,  "width" : 50,  "align" : "left",  "valueGetter" : "id", "isEditable" : False}),
            ("kind"    , {"title" : "Kind",             "minimumWidth" : 100, "width" : 100, "align" : "left",  "valueGetter" : "kind", "isEditable" : False}),
            ("label"   , {"title" : "Label",            "minimumWidth" : 100, "width" : 100, "align" : "left",  "valueGetter" : "listctrl_label", "isEditable" : False, "isSpaceFilling" : True}),
            ("mass"    , {"title" : "Mass [g]",         "minimumWidth" : 140, "width" : 140, "align" : "right", "valueGetter" : "mass", "isEditable" : False, "stringConverter" : "%.4f"}),
            ("moles"   , {"title" : "Moles",            "minimumWidth" : 90,  "width" : 90,  "align" : "right", "valueGetter" : "moles", "isEditable" : True, "stringConverter" : "%.4f"}),
            ("molwt"   , {"title" : "Molecular Weight", "minimumWidth" : 120, "width" : 120, "align" : "right", "valueGetter" : "molwt", "isEditable" : False, "stringConverter" : "%.4f"}),
            ("name"    , {"title" : "Name",             "minimumWidth" : 200, "width" : 200, "align" : "left",  "valueGetter" : "name", "isEditable" : False, "isSpaceFilling" : True}),
            ("pk"      , {"title" : "pK",               "minimumWidth" : 100, "width" : 120, "align" : "right", "valueGetter" : "pk", "isEditable" : False, "stringConverter" : "%.2f"}),
            ("physform", {"title" : "Physical Form",    "minimumWidth" : 150, "width" : 150, "align" : "left",  "valueGetter" : "physical_form", "isEditable" : False}),
            ("reaction", {"title" : "Reaction",         "minimumWidth" : 200, "width" : 200, "align" : "left",  "valueGetter" : "reaction", "isEditable" : False}),
            ("scaled"  , {"title" : "Scaled Mass [g]",  "minimumWidth" : 140, "width" : 140, "align" : "right", "valueGetter" : "mass", "isEditable" : False, "stringConverter" : "%.4f"}),
            ("short"   , {"title" : "Short name",       "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "short_name", "isEditable" : False}),
            ("smiles"  , {"title" : "SMILES",           "minimumWidth" : 120, "width" : 120, "align" : "left",  "valueGetter" : "smiles", "isEditable" : False}),
        ])

        self.model = BatchCalculator()

        main_panel = wx.Panel(self)
        self.inppanel = InputPanel(main_panel, self.model, self.columns)
        self.outpanel = OutputPanel(main_panel, self.model, self.columns)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.inppanel, 1, flag=wx.CENTER|wx.EXPAND)
        vbox.Add(self.outpanel, 1, flag=wx.CENTER|wx.EXPAND)
        main_panel.SetSizer(vbox)
        main_panel.Fit()

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
        calcm = wx.Menu()
        minvcalc = calcm.Append(wx.ID_ANY, "Calculate composition", "CC")
        menubar.Append(calcm, "Calculation")
        # Database Menu
        dbm = wx.Menu()
        mchangedb = dbm.Append(wx.ID_ANY, "Change db\t", "Switch to a different database")
        dbm.AppendSeparator()
        maddchemicaldb = dbm.Append(wx.ID_ANY, "Edit Chemicals\t", "Edit chemicals records in the database")
        maddcomponentdb = dbm.Append(wx.ID_ANY, "Edit Components\t", "Edit zeolite component records in the database")
        maddbatchdb = dbm.Append(wx.ID_ANY, "Edit Batch\t", "Edit batch records in the database")
        maddreactiondb = dbm.Append(wx.ID_ANY, "Edit Reactions\t", "Edit reaction records in the database")
        maddcategorydb = dbm.Append(wx.ID_ANY, "Edit Categories\t", "Edit category records in the database")
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
        self.Bind(wx.EVT_MENU, self.OnInverseCalculation, minvcalc)
        self.Bind(wx.EVT_MENU, self.OnShowB, mshowb)
        self.Bind(wx.EVT_MENU, self.OnExportTex, metex)
        self.Bind(wx.EVT_MENU, self.OnChangeDB, mchangedb)
        self.Bind(wx.EVT_MENU, self.OnAddChemicalToDB, maddchemicaldb)
        self.Bind(wx.EVT_MENU, self.OnAddComponentToDB, maddcomponentdb)
        self.Bind(wx.EVT_MENU, self.OnAddBatchToDB, maddbatchdb)
        self.Bind(wx.EVT_MENU, self.OnAddReactionToDB, maddreactiondb)
        self.Bind(wx.EVT_MENU, self.OnAddCategoryToDB, maddcategorydb)
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
            self.model.new_dbsession(path)
        dlg.Destroy()

    def OnExit(self, event):
        self.Close()

    def OnExportTex(self, event):
        '''
        Open the dialog with options about the TeX document tobe written.
        '''
        etexdialog = dialogs.ExportTexDialog(parent=self, id=-1)
        result = etexdialog.ShowModal()
        if result == wx.ID_OK:
            flags = etexdialog.get_data()
            # get the string with contents of the TeX report
            tex = get_report_as_string(flags, self.model)
            self.OnSaveTeX(tex, flags['typeset'], flags['pdflatex'])

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
                    self.model.chemicals,
                    self.model.A, self.model.B, self.model.X,
                    self.model.scale_all, self.model.sample_scale,
                    self.model.sample_size, self.model.selections)
            fp = file(path, 'wb') # Create file anew
            pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)
            fp.close()

        dlg.Destroy()

    def OnSaveTeX(self, texdata, typeset, pdflatex):

        texwildcard =  "TeX Files (*.tex)|*tex|"     \
                       "All files (*.*)|*.*"

        opts = "-halt-on-error"

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

    def update_all_objectlistviews(self):
        '''
        Update all the ObjectListView with the current state of the model.
        '''

        self.inppanel.compOlv.SetObjects(self.model.components)
        self.inppanel.reacOlv.SetObjects(self.model.chemicals)
        self.outpanel.resultOlv.SetObjects(self.model.chemicals)
        self.outpanel.scaledOlv.SetObjects(self.model.chemicals)

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
        #sys.excepthook = ExceptionHook
        self.SetTopWindow(self.frame)
        self.frame.Show()

        return True

if __name__ == "__main__":

    app = ZeoGui(False)
    # uncomment for debugging
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
