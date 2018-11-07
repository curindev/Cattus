# method.py
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


"""Importando modulos necesarios"""

import gi, os
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, GtkSource
from datetime import datetime, time as datetime_time, timedelta

"""Metodos globales para los widgets"""

def set_widget_image(widget, icon):
    image = Gtk.Image()
    image.set_from_file(icon)
    widget.set_image(image)
    

def set_treeview_configuration(widget):
    widget.columns_autosize()
    widget.set_grid_lines(Gtk.TreeViewGridLines.BOTH)    
    
def set_sourceview_configuration(widget, editable=False):
    lenguage_managuer = GtkSource.LanguageManager()
    lenguage = lenguage_managuer.get_language("sql")
    buffer = widget.get_buffer()
    buffer.set_highlight_syntax(True)
    buffer.set_language(lenguage)      
        
    widget.set_show_line_numbers(True)
    
 
def get_time_difference(start, end):
    if isinstance(str(start), datetime_time):
        assert isinstance(str(end), datetime_time)
        start, end = [datetime.combine(datetime.min, t) for t in [start, end]]
    if start <= end: 
        return str(end - start)
    else:
        end += timedelta(1)
        assert end > start
        return str(end - start)        
       
    
