# source.py
#
# Copyright 2018 Jose
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, GtkSource
import os
    
class LogView(Gtk.ScrolledWindow):
    def __init__(self):
        super().__init__()
        self.LOG_MODEL = None        
        self.create_log()
        
    def create_log(self):
        self.LOG_MODEL = Gtk.ListStore(str, str, str, str, str, str)
        columnNumber = Gtk.TreeViewColumn("N", Gtk.CellRendererText(), text=0)
        columnQuery = Gtk.TreeViewColumn("QUERY", Gtk.CellRendererText(), text=1)
        columnStatus = Gtk.TreeViewColumn("STATUS", Gtk.CellRendererText(), text=2)                
        columnMessage = Gtk.TreeViewColumn("MESSAGE", Gtk.CellRendererText(), text=3)                
        columnTime = Gtk.TreeViewColumn("TIME", Gtk.CellRendererText(), text=4)        
        columnFrom = Gtk.TreeViewColumn("FROM", Gtk.CellRendererText(), text=5)                        
        treeview = Gtk.TreeView()  
        treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)   
        treeview.columns_autosize()
        treeview.append_column(columnNumber)
        treeview.append_column(columnQuery)
        treeview.append_column(columnStatus)
        treeview.append_column(columnMessage)        
        treeview.append_column(columnTime)
        treeview.append_column(columnFrom)        
        treeview.set_model(self.LOG_MODEL)
            
        self.add(treeview)        
        
    def get_model(self):
        return self.LOG_MODEL



class SourceText(Gtk.ScrolledWindow):
    def __init__(self, notebookEditor):
        super().__init__()
        self.notebookEditor = notebookEditor
        self.create_view()
        
    def create_view(self):
        sourceview = GtkSource.View()
        sourceviewBuffer = sourceview.get_buffer()
        sourceviewBuffer.connect("changed", self.on_buffer_editor_change)
        self.add_sintaxis_sqlite_so_editor(sourceview.get_buffer())
        sourceview.set_show_line_numbers(True)
        sourceview.set_tab_width(4)
        sourceview.set_auto_indent(True)
        sourceview.set_insert_spaces_instead_of_tabs(True)
        sourceview.set_highlight_current_line(True)
        sourceview.set_indent_on_tab(True)
        
        self.set_tooltip_text("untitled {0}".format(self.notebookEditor.get_n_pages()+1))
        self.add(sourceview)                                
        
    def add_sintaxis_sqlite_so_editor(self, buffer):  
        lenguage_managuer = GtkSource.LanguageManager()
        lenguage = lenguage_managuer.get_language("sql")
        buffer.set_highlight_syntax(True)
        buffer.set_language(lenguage)        
    
        
    def on_buffer_editor_change(self, widget):            
        widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())        
        path, filename = os.path.split(widget.get_tooltip_text())
        self.notebookEditor.set_tab_label(widget, Gtk.Label("*"+filename))    
        
