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


import os
import sys

from ObjectListView import ObjectListView

import wx
import wx.lib.agw.genericmessagedialog as GMD


__version__ = "0.2.2"


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


class ExceptionDialog(GMD.GenericMessageDialog):

    def __init__(self, msg):
        '''constructor'''
        GMD.GenericMessageDialog.__init__(self, None, msg, "Exception!",
                                          wx.OK | wx.ICON_ERROR)


class ExportPdfMinimalDialog(wx.Dialog):
    '''
    A dialog for setting the options of the pdf report.
    '''

    def __init__(self, parent, id=wx.ID_ANY, title="",
                 pos=wx.DefaultPosition, size=(400, 550),
                 style=wx.DEFAULT_FRAME_STYLE, name="Export PDF Dialog"):

        super(ExportPdfMinimalDialog, self).__init__(parent, id, title, pos,
                                                     size, style, name)

        panel = wx.Panel(self)

        top_lbl = wx.StaticText(panel, -1, "PDF document options")
        top_lbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        title_lbl = wx.StaticText(panel, -1, "Title:")
        title = wx.TextCtrl(panel, -1, "")
        author_lbl = wx.StaticText(panel, -1, "Author:")
        author = wx.TextCtrl(panel, -1, "")
        comment_lbl = wx.StaticText(panel, -1, "Comment:")
        comment = wx.TextCtrl(panel, -1, "", size=(-1, 100),
                              style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)

        export_btn = wx.Button(panel, id=wx.ID_OK, label="Export")
        cancel_btn = wx.Button(panel, id=wx.ID_CANCEL)

        self.widgets = {
            "title": title,
            "author": author,
            "comment": comment,
        }

        # layout

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(top_lbl, 0, wx.ALL, 5)
        main_sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        fgs_title = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        fgs_title.AddGrowableCol(1)
        fgs_title.Add(title_lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(title, 0, wx.EXPAND)
        fgs_title.Add(author_lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(author, 0, wx.EXPAND)
        fgs_title.Add(comment_lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(comment, 0, wx.GROW)

        main_sizer.Add(fgs_title, 0, wx.EXPAND | wx.ALL, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(cancel_btn, 0, wx.LEFT | wx.RIGHT, 10)
        hbox.Add(export_btn, 0, wx.LEFT | wx.RIGHT, 10)

        main_sizer.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT, 10)
        panel.SetSizerAndFit(main_sizer)

    def get_data(self):

        res = dict()
        for name, attr in self.widgets.items():
            res[name] = attr.GetValue()
        return res


class ExportPdfDialog(wx.Dialog):
    '''
    A dialog for setting the options of the pdf report (using reportlab).
    '''

    def __init__(self, parent, id=wx.ID_ANY, title="", record=None,
                 pos=wx.DefaultPosition, size=(420, 450),
                 style=wx.DEFAULT_FRAME_STYLE, name="Export Pdf Dialog"):

        super(ExportPdfDialog, self).__init__(parent, id, title, pos, size,
                                              style, name)

        if record is None:
            title = ""
            author = ""
        else:
            title = record.name
            author = record.laborant

        panel = wx.Panel(self)

        top_lbl = wx.StaticText(panel, -1, "PDF document options")
        top_lbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        title_lbl = wx.StaticText(panel, -1, "Title:")
        title = wx.TextCtrl(panel, -1, title)
        author_lbl = wx.StaticText(panel, -1, "Author:")
        author = wx.TextCtrl(panel, -1, author)
        comment_lbl = wx.StaticText(panel, -1, "Comment:")
        comment = wx.TextCtrl(panel, -1, "", size=(-1, 100),
                              style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)

        export_btn = wx.Button(panel, id=wx.ID_OK, label="Export")
        cancel_btn = wx.Button(panel, id=wx.ID_CANCEL)

        cb_cmpm = wx.CheckBox(panel, label="Composition Matrix")
        cb_bmat = wx.CheckBox(panel, label="Batch Matrix")
        cb_rescaleAll = wx.CheckBox(panel,
                                label="Result vector X (rescaled by a factor)")
        cb_rescaleTo = wx.CheckBox(panel,
                                label="Result vector X (rescaled to the sample size)")
        cb_rescaleItem = wx.CheckBox(panel,
                                label="Result vector X (rescaled to an item)")

        cb_cmpm.SetValue(True)
        cb_bmat.SetValue(True)
        cb_rescaleAll.SetValue(True)
        cb_rescaleTo.SetValue(True)
        cb_rescaleItem.SetValue(True)

        sb_calculation = wx.StaticBox(panel, label="Include")
        sbc_bs = wx.StaticBoxSizer(sb_calculation, wx.VERTICAL)
        sbc_bs.Add(cb_cmpm, flag=wx.LEFT | wx.TOP, border=5)
        sbc_bs.Add(cb_bmat, flag=wx.LEFT | wx.TOP, border=5)
        sbc_bs.Add(cb_rescaleAll, flag=wx.LEFT | wx.TOP, border=5)
        sbc_bs.Add(cb_rescaleTo, flag=wx.LEFT | wx.TOP, border=5)
        sbc_bs.Add(cb_rescaleItem, flag=wx.LEFT | wx.TOP, border=5)

        self.widgets = {
            "title": title,
            "author": author,
            "comment": comment,
            "composition": cb_cmpm,
            "batch": cb_bmat,
            "rescale_all": cb_rescaleAll,
            "rescale_to": cb_rescaleTo,
            "rescale_item": cb_rescaleItem,
        }

        # layout

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(top_lbl, 0, wx.ALL, 5)
        main_sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        fgs_title = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        fgs_title.AddGrowableCol(1)
        fgs_title.Add(title_lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(title, 0, wx.EXPAND)
        fgs_title.Add(author_lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(author, 0, wx.EXPAND)
        fgs_title.Add(comment_lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(comment, 0, wx.GROW)

        main_sizer.Add(fgs_title, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(sbc_bs, 0, wx.EXPAND | wx.ALL, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(cancel_btn, 0, wx.LEFT | wx.RIGHT, 10)
        hbox.Add(export_btn, 0, wx.LEFT | wx.RIGHT, 10)

        main_sizer.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT, 10)
        panel.SetSizerAndFit(main_sizer)

    def get_data(self):

        res = dict()
        for name, attr in self.widgets.items():
            res[name] = attr.GetValue()
        return res


class ExportTexDialog(wx.Dialog):
    '''
    A dialog for setting the options of the tex report.
    '''

    def __init__(self, parent, id=wx.ID_ANY, title="",
                 pos=wx.DefaultPosition, size=(400, 650),
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
        comment_lbl = wx.StaticText(panel, -1, "Comment:")
        comment = wx.TextCtrl(panel, -1, "", size=(-1, 100),
                              style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)

        export_btn = wx.Button(panel, id=wx.ID_OK, label="Export")
        cancel_btn = wx.Button(panel, id=wx.ID_CANCEL)

        cb_cmpm = wx.CheckBox(panel, label="Composition Matrix")
        cb_bmat = wx.CheckBox(panel, label="Batch Matrix")
        cb_rescaleAll = wx.CheckBox(panel,
                            label="Result vector X (rescaled by a factor)")
        cb_rescaleTo = wx.CheckBox(panel,
                            label="Result vector X (rescaled to the sample size)")

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
        sbc_bs.Add(cb_cmpm, flag=wx.LEFT | wx.TOP, border=5)
        sbc_bs.Add(cb_bmat, flag=wx.LEFT | wx.TOP, border=5)
        sbc_bs.Add(cb_rescaleAll, flag=wx.LEFT | wx.TOP, border=5)
        sbc_bs.Add(cb_rescaleTo, flag=wx.LEFT | wx.TOP, border=5)

        sb_synthesis = wx.StaticBox(panel, label="Synthesis")
        sbs_bs = wx.StaticBoxSizer(sb_synthesis, wx.VERTICAL)
        sbs_bs.Add(cb_calo, flag=wx.LEFT | wx.TOP, border=5)
        sbs_bs.Add(cb_ione, flag=wx.LEFT | wx.TOP, border=5)
        sbs_bs.Add(cb_calt, flag=wx.LEFT | wx.TOP, border=5)

        sb_analysis = wx.StaticBox(panel, label="Analysis")
        sba_bs = wx.StaticBoxSizer(sb_analysis, wx.VERTICAL)
        sba_bs.Add(cb_xrd, flag=wx.LEFT | wx.TOP, border=5)
        sba_bs.Add(cb_sem, flag=wx.LEFT | wx.TOP, border=5)

        self.widgets = {
            "title": title,
            "author": author,
            "email": email,
            "comment": comment,
            "composition": cb_cmpm,
            "batch": cb_bmat,
            "rescale_all": cb_rescaleAll,
            "rescale_to": cb_rescaleTo,
            "calcination_i": cb_calo,
            "ion_exchange": cb_ione,
            "calcination_ii": cb_calt,
            "xrd": cb_xrd,
            "sem": cb_sem,
            "typeset": cb_pdf,
            "pdflatex": self.pdflatex,
        }

        # layout

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(top_lbl, 0, wx.ALL, 5)
        main_sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        fgs_title = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        fgs_title.AddGrowableCol(1)
        fgs_title.Add(title_lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(title, 0, wx.EXPAND)
        fgs_title.Add(author_lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(author, 0, wx.EXPAND)
        fgs_title.Add(email_lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(email, 0, wx.EXPAND)
        fgs_title.Add(comment_lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        fgs_title.Add(comment, 0, wx.GROW)

        main_sizer.Add(fgs_title, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(sbc_bs, 0, wx.EXPAND | wx.ALL, 10)

        gbs = wx.GridBagSizer(hgap=5, vgap=5)
        gbs.Add(sbs_bs, pos=(0, 0), flag=wx.ALIGN_RIGHT | wx.GROW | wx.ALL,
                border=10)
        gbs.Add(sba_bs, pos=(0, 1), flag=wx.ALIGN_LEFT | wx.EXPAND | wx.ALL,
                border=10)
        gbs.AddGrowableCol(0)
        gbs.AddGrowableCol(1)

        main_sizer.Add(gbs, 0, wx.EXPAND | wx.ALL, border=10)

        fgs0 = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        fgs0.AddGrowableCol(1)
        fgs0.Add(cb_pdf, flag=wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM,
                 border=10)
        fgs0.Add(self.pdflatex, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                 border=10)
        main_sizer.Add(fgs0, flag=wx.EXPAND | wx.ALL, border=5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(cancel_btn, 0, wx.LEFT | wx.RIGHT, 10)
        hbox.Add(export_btn, 0, wx.LEFT | wx.RIGHT, 10)

        main_sizer.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT, 10)
        panel.SetSizerAndFit(main_sizer)

        # events

        cb_pdf.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox)

    def EvtCheckBox(self, event):
        cb = event.GetEventObject()
        if cb.IsChecked():
            self.pdflatex.Enable(True)

    def get_data(self):

        res = dict()
        for name, attr in self.widgets.items():
            res[name] = attr.GetValue()
        return res


class RescaleToItemDialog(wx.Dialog):

    def __init__(self, parent, objects, cols=None, id=wx.ID_ANY,
                 title="Choose an item and the amount",
                 pos=wx.DefaultPosition, size=(400, 400),
                 style=wx.DEFAULT_FRAME_STYLE, name="Rescale to Item Dialog"):
        '''
        A dialog to get the selected objects (components or chemicals) and the
        amount (moles or grams). The dialog is used in the conventional batch
        calculation (moles to masses) as well as in the inverse (masses to
        moles).
        '''

        super(RescaleToItemDialog, self).__init__(parent, id, title, pos, size,
                                                  style, name)

        panel = wx.Panel(self)

        self.olv = ObjectListView(panel, wx.ID_ANY,
                                  style=wx.LC_REPORT | wx.SUNKEN_BORDER,
                                  useAlternateBackColors=True)
        self.olv.evenRowsBackColor = "#DCF0C7"
        self.olv.oddRowsBackColor = "#FFFFFF"

        self.SetObjects(objects, cols)

        scalelbl = wx.StaticText(panel, -1, "Amount:")
        self.amount = wx.TextCtrl(panel, -1, "{0:6.2f}".format(1.0).strip())

        buttonOk = wx.Button(panel, id=wx.ID_OK)
        buttonOk.SetDefault()
        buttonCancel = wx.Button(panel, id=wx.ID_CANCEL)

        # layout

        sizer = wx.GridBagSizer(vgap=5, hgap=5)
        sizer.Add(self.olv, pos=(0, 0), span=(1, 4), flag=wx.GROW | wx.ALL,
                  border=5)
        sizer.Add(scalelbl,  pos=(1, 0),
                  flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                  border=10)
        sizer.Add(self.amount, pos=(1, 1), span=(1, 2),
                  flag=wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT | wx.BOTTOM,
                  border=10)
        sizer.Add(buttonCancel, pos=(2, 2), flag=wx.BOTTOM, border=10)
        sizer.Add(buttonOk, pos=(2, 3), flag=wx.BOTTOM | wx.RIGHT, border=10)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(0)
        panel.SetSizer(sizer)

    def SetObjects(self, objects, cols):
        '''Set the OLV columns and put current objects in the OLV'''

        self.olv.SetColumns(cols)
        self.olv.CreateCheckStateColumn()
        self.olv.SetObjects(objects)

    def GetCurrentSelections(self):
        '''Return the entered amount and objects selected in the dialog.'''

        return self.amount.GetValue(), self.olv.GetCheckedObjects()


class RescaleToSampleDialog(wx.Dialog):

    def __init__(self, parent, model, cols=None, id=wx.ID_ANY,
                 title="Choose compounds and sample size ...",
                 pos=wx.DefaultPosition, size=(400, 400),
                 style=wx.DEFAULT_FRAME_STYLE,
                 name="Rescale to Sample Dialog"):

        super(RescaleToSampleDialog, self).__init__(parent, id, title, pos,
                                                    size, style, name)

        panel = wx.Panel(self)

        self.olv = ObjectListView(panel, wx.ID_ANY,
                                  style=wx.LC_REPORT | wx.SUNKEN_BORDER,
                                  useAlternateBackColors=True)
        self.olv.evenRowsBackColor = "#DCF0C7"
        self.olv.oddRowsBackColor = "#FFFFFF"

        self.SetChemicals(model, cols)

        scalelbl = wx.StaticText(panel, -1, "Sample size [g]:")
        self.sample_size = wx.TextCtrl(panel, -1, str(model.sample_size))

        buttonOk = wx.Button(panel, id=wx.ID_OK)
        buttonOk.SetDefault()
        buttonCancel = wx.Button(panel, id=wx.ID_CANCEL)

        # layout

        sizer = wx.GridBagSizer(vgap=5, hgap=5)
        sizer.Add(self.olv, pos=(0, 0), span=(1, 4), flag=wx.GROW | wx.ALL,
                  border=5)
        sizer.Add(scalelbl, pos=(1, 0),
                  flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                  border=10)
        sizer.Add(self.sample_size, pos=(1, 1), span=(1, 2),
                  flag=wx.EXPAND | wx.ALIGN_LEFT | wx.RIGHT | wx.BOTTOM,
                  border=10)
        sizer.Add(buttonCancel, pos=(2, 2), flag=wx.BOTTOM, border=10)
        sizer.Add(buttonOk, pos=(2, 3), flag=wx.BOTTOM | wx.RIGHT, border=10)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(0)
        panel.SetSizer(sizer)

    def SetChemicals(self, model, cols):
        '''Set the OLV columns and put current chemicals in the OLV'''

        self.olv.SetColumns(cols)
        self.olv.CreateCheckStateColumn()
        for item in model.chemicals:
            self.olv.Check(item)
        self.olv.SetObjects(model.chemicals)

    def GetCurrentSelections(self):
        '''
        Return the entered sample size and objects selected in the dialog.
        '''

        return self.sample_size.GetValue(), self.olv.GetCheckedObjects()


def show_message_dlg(message, caption, flag=wx.ICON_ERROR | wx.OK):
    """"""
    msg = wx.MessageDialog(None, message=message,
                           caption=caption, style=flag)
    msg.ShowModal()
    msg.Destroy()


# Validators


class NumberValidator(wx.PyValidator):

    def __init__(self):
        wx.PyValidator.__init__(self)

    def Clone(self):
        """
        Note that every validator must implement the Clone() method.
        """
        return NumberValidator()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        if len(text) == 0:
            wx.MessageBox("This field must contain some text!", "Error")
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(
            wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True


class NonEmptyValidator(wx.PyValidator):

    def __init__(self):
        wx.PyValidator.__init__(self)
        print "called validator"

    def Clone(self):
        """
        Note that every validator must implement the Clone() method.
        """
        return NonEmptyValidator()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        print "len(text) = ", len(text)
        if len(text) == 0:
            wx.MessageBox("This field must contain some text!", "Error")
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(
            wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True


class TextObjectValidator(wx.PyValidator):
    """
    This validator is used to ensure that the user has entered something
    into the text object editor dialog's text field.
    """

    def __init__(self):
        """
        Standard constructor.
        """

        wx.PyValidator.__init__(self)

    def Clone(self):
        """
        Standard cloner.

        Note that every validator must implement the Clone() method.
        """
        return TextObjectValidator()

    def Validate(self, win):
        """ Validate the contents of the given text control.
        """

        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()

        if len(text) == 0:
            wx.MessageBox("A text object must contain some text!", "Error")
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True

    def TransferToWindow(self):
        """ Transfer data from validator to window.
            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        """ Transfer data from window to validator.
            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.
