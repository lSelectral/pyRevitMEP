"""
Copyright (c) 2017 Cyril Waechter
Python scripts for Autodesk Revit

This file is part of pyRevitMEP repository at https://github.com/CyrilWaechter/pyRevitMEP

pyRevitMEP is an extension for pyRevit. It contain free set of scripts for Autodesk Revit:
you can redistribute it and/or modify it under the terms of the GNU General Public License
version 3, as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

See this link for a copy of the GNU General Public License protecting this package.
https://github.com/CyrilWaechter/pyRevitMEP/blob/master/LICENSE
"""
from revitutils import doc, selection
from scriptutils.userinput import WPFWindow

# noinspection PyUnresolvedReferences
from Autodesk.Revit.DB import Transaction, Element, BuiltInParameter, FilteredElementCollector, ViewPlan
# noinspection PyUnresolvedReferences
from Autodesk.Revit import Exceptions

__doc__ = "Rename selected views according to a specific convention"
__title__ = "Rename views"
__author__ = "Cyril Waechter"

try:
    t = Transaction(doc, "Rename views")
    t.Start()
    for view in selection.elements:  # Loop trough selected views
        view_typeid = doc.GetElement(view.GetTypeId())  # Get ViewFamilyType Id
        view_typename = Element.Name.GetValue(view_typeid)  # Get ViewFamilyType Name

        # Get Scope Box name if it exist
        try:
            view_scopebox = view.get_Parameter(BuiltInParameter.VIEWER_VOLUME_OF_INTEREST_CROP)
            view_scopebox_name = "" if view_scopebox.Value() is None else "_" + view_scopebox.AsValueString()
        except AttributeError:
            view_scopebox_name = ""

        # Get view reference level if it exist
        view_genlevel = "" if view.GenLevel is None else view.GenLevel.Name

        # Future view name
        view_name = "{c}_{a}{b}".format(a=view_genlevel, b=view_scopebox_name, c=view_typename, )

        # Rename view
        i = 0
        while True:
            try:
                view.Name = view_name if i == 0 else view_name + str(i)
            except Exceptions.ArgumentException:
                i += 1
            except:
                raise
            else:
                break
    t.Commit()
except:  # print a stack trace and error messages for debugging
    import traceback
    traceback.print_exc()
    t.RollBack()

def get_viewparameters(viewclass):
    view = FilteredElementCollector(doc).OfClass(viewclass).FirstElement().Parameters
    for param in view.Parameters:
        print(param.Definition.Name)
        print(param.Definition.BuiltInParameter)
        if param.IsShared:
            print(param.GUID)
        print param.AsValueString()



class ViewRename(WPFWindow):
    """
    GUI used to select a reference level from a list or an object
    """

    def __init__(self, xaml_file_name):
        WPFWindow.__init__(self, xaml_file_name)

        # self.combobox_parameters.ItemsSource = get_viewparameters(ViewPlan)
        self.viewname_preview = self.pattern.Text
        self.preview.DataContext = self.viewname_preview
        self.cursorposition = 0
        self.cb_all.IsChecked = None

    def button_addparameter_click(self, sender, e):
        parameter = "test"
        self.pattern.Text = self.pattern.Text[:self.cursorposition]+parameter+self.pattern.Text[self.cursorposition:]

    def pattern_SelectionChanged(self, sender, e):
        self.cursorposition = sender.SelectionStart
        print sender.Text
        self.preview.DataContext = self.pattern.Text

    def cb_CheckedChanged(self, sender, e):
        self.cb_all.IsChecked = None
        if self.cb_viewplan.IsChecked == True and self.cb_view3D.IsChecked == True and self.cb_viewsection.IsChecked == True :
            self.cb_all.IsChecked = True
        if self.cb_viewplan.IsChecked == False and self.cb_view3D.IsChecked == False and self.cb_viewsection.IsChecked == False :
            self.cb_all.IsChecked = False

    def cb_all_CheckedChanged(self, sender, e):
        checked = self.cb_all.IsChecked
        self.cb_viewplan.IsChecked = checked
        self.cb_view3D.IsChecked = checked
        self.cb_viewsection.IsChecked = checked

ViewRename('ViewRename.xaml').ShowDialog()
