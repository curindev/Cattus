# notebook.py
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

from gi.repository import Gtk, Gdk


class DynamicNotebook(Gtk.Notebook):
    def __init__(self):
        super().__init__()
        self.TITLE_PATH = None
        self.NUMBER_TAB_EDITOR = 0
        self.NUMBER_TAB_LOGGER = 0
        Gtk.Notebook.add_events(self, Gdk.EventMask.SCROLL_MASK | Gdk.EventMask.SMOOTH_SCROLL_MASK)
        Gtk.Notebook.connect(self, "scroll-event", self.on_action_scroll_notebook_editor)

# Override widget functions

    def append_page(self, child, tab_label):
        self.TITLE_PATH = tab_label
        Gtk.Notebook.append_page(self, child, self.init_tab_closeable(child, tab_label))        
        
    def append_page_logger(self, child, tab_label):
        self.TITLE_PATH = tab_label
        Gtk.Notebook.append_page(self, child, self.init_tab_closeable_logger(child, tab_label))             
        
    def append_page_fixed(self, child, tab_label):
        self.TITLE_PATH = tab_label
        Gtk.Notebook.append_page(self, child, tab_label)        

    def insert_page(self, child, tab_label, position):
        Gtk.Notebook.insert_page(self, child, self.init_tab_closeable(child,tab_label), position)
    
    def set_tab_label(self, child, tab_label):    
        Gtk.Notebook.set_tab_label(self,child, self.init_tab_label(child, tab_label))
    
        
    def on_action_scroll_notebook_editor(self, widget, event):
        if event.get_scroll_deltas()[2] < 0:
            Gtk.Notebook.prev_page(self)
        else:
            Gtk.Notebook.next_page(self)
            

#widget extra functions
    def init_tab_closeable_logger(self, widget, tab_label):      
        self.NUMBER_TAB_LOGGER += 1
      
        tab_label.set_text(tab_label.get_text()+" {0}".format(self.NUMBER_TAB_LOGGER))
        btn_close = Gtk.Button("x")
        btn_close.set_relief(Gtk.ReliefStyle.NONE)
        btn_close.set_focus_on_click(False)

        box_widget = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        box_widget.pack_start(tab_label, False, True, 0)
        box_widget.pack_start(btn_close, False, True, 0)

        btn_close.connect("clicked", self.on_action_close_tab, widget)
        box_widget.show_all()
        return box_widget
        
        
    def init_tab_closeable(self, widget, tab_label):
        self.NUMBER_TAB_EDITOR += 1
        
        tab_label.set_text(tab_label.get_text()+" {0}".format(self.NUMBER_TAB_EDITOR))
        btn_close = Gtk.Button("x")
        btn_close.set_relief(Gtk.ReliefStyle.NONE)
        btn_close.set_focus_on_click(False)

        box_widget = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        box_widget.pack_start(tab_label, False, True, 0)
        box_widget.pack_start(btn_close, False, True, 0)

        btn_close.connect("clicked", self.on_action_close_tab, widget)
        box_widget.show_all()
        return box_widget
        
    def init_tab_label(self, widget, tab_label):
        btn_close = Gtk.Button("x")
        btn_close.set_relief(Gtk.ReliefStyle.NONE)
        btn_close.set_focus_on_click(False)

        box_widget = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        box_widget.pack_start(tab_label, False, True, 0)
        box_widget.pack_start(btn_close, False, True, 0)

        btn_close.connect("clicked", self.on_action_close_tab, widget)
        box_widget.show_all()
        return box_widget        
        
#    def get_path_title(self):
#        return self.TITLE_PATH.get_text()
#    
#    
#    def set_path_title(self, title):
#        self.TITLE_PATH.set_text(title)


#widget events
    def on_action_close_tab(self, sender, widget):
        self.remove_page(self.page_num(widget))

