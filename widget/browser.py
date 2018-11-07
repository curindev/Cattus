# treeview.py
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

import gi, os, sqlite3
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, GtkSource
from datetime import datetime, time as datetime_time, timedelta
from widget.connection import SQLMeta, SQLUtils
from widget.resource import *
from widget.method import *

"""Clase para mostrar los datos de las tablas"""
class BrowserView(Gtk.Box):
    def __init__(self, CURRENT_DATABASE, myAccelerators):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)    
        
        """Asignando las variables globales"""            
        self.CURRENT_DATABASE = CURRENT_DATABASE
        self.myAccelerators = myAccelerators
        
        """Declarando variables para acceder a la information de la base de datos"""        
        self.meta = SQLMeta()
        self.sqlUtils = SQLUtils()        
        
        """Declarando variables auxiliares"""        
        self.numberColumn = 0
        self.START_TIME = None
        self.END_TIME = None
        self.DIFERENCE_TIME = None        
        self.scrollTreeView = None
        self.treeview = None
        self.model = None
        self.modelFilter = None
                
        """"Obteniendo los objetos de la ui"""                
        builder = Gtk.Builder()
        builder.add_from_file(UI_BROWSER)
        self.boxRoot = builder.get_object("boxRoot")
        self.entrySearchTreeView = builder.get_object("entrySearchTreeView")
        self.entryColumnTreeView = builder.get_object("entryColumnTreeView") 
        self.entryGoToTreeView = builder.get_object("entryGoToTreeView")
        self.comboxTables = builder.get_object("comboxTables")
        self.buttonRefresh = builder.get_object("buttonRefresh")   
        self.boxTreeView = builder.get_object("boxTreeView")
        self.labelColumns = builder.get_object("labelColumns")
        self.labelRows = builder.get_object("labelRows")
        self.labelTime = builder.get_object("labelTime")             
        
        """Añadiendo iconos a los botones"""
        set_widget_image(self.buttonRefresh,ICON_REFRESH)                
        
        """Añadiendo combinaciones de teclas para los botones"""
        self.add_accelerator_widget(self.comboxTables, "<Alt>T", signal="popup")         
        self.add_accelerator_widget(self.buttonRefresh, "<Alt>R", signal="clicked")
        
        """Añadiendo metodos para los widgets"""
        self.entrySearchTreeView.connect("changed", self.on_action_changed_search_treeview)
        self.entryColumnTreeView.connect("value-changed", self.on_action_column_entry_changed)
        self.entryGoToTreeView.connect("insert_text", self.on_action_go_to_entry_validation)
        self.entryGoToTreeView.connect("activate", self.on_action_go_to_entry)
        self.comboxTables.connect("popup", self.on_action_popdown_combobox)                       
        self.buttonRefresh.connect("clicked", self.on_action_button_refresh_clicked)
        self.comboxTables.connect("changed", self.on_combobox_change_item)
        
        """Cargando la interfaz grafica"""         
        self.init_gui()
        self.pack_start(self.boxRoot, True, True, 0)       
        
    """Metodo para cargar la interfaz"""        
    def init_gui(self):
        self.meta.connect(self.CURRENT_DATABASE)
        tables = self.meta.get_name_from_master('table')
        count = 0
        for table in self.sqlUtils.convert_tuple_to_list(tables):
            self.comboxTables.append(str(count), table[0])
            count +=1
         
        self.meta.disconnect()
        
    """Metodo para actualizar el treeview cuando el combobox cambia"""
    def on_combobox_change_item(self, widget):
        if widget.get_active_text() is not None:
            try:
                for child in self.boxTreeView.get_children():
                    child.destroy()
                    
                self.scrollTreeView = Gtk.ScrolledWindow()
                self.treeview = Gtk.TreeView()
                set_treeview_configuration(self.treeview)
                
                self.scrollTreeView.add(self.treeview)
                self.boxTreeView.pack_start(self.scrollTreeView, True, True, 0)
                
                self.meta.connect(self.CURRENT_DATABASE)
                
                self.START_TIME = datetime.now()
                
                info = self.meta.get_table_info(widget.get_active_text())
                columns = []
                count = 0
                for item in info:
                    columns.append([str(item[1])])
                    count +=1
                    
                self.entryColumnTreeView.get_adjustment().configure(0, 0, (count-1),1,10,0)
                    
                self.model = Gtk.ListStore(*[str]* count)
                self.modelFilter = self.model.filter_new()
                self.treeview.set_model(self.modelFilter)
                self.modelFilter.set_visible_func(self.match_func)
                
                count = 0
                for i in columns:
                    column = Gtk.TreeViewColumn(i[0], Gtk.CellRendererText(), text=count)
                    count +=1
                    self.treeview.append_column(column)        
                self.labelColumns.set_text(str(count))
                
                
                data = self.meta.get_select_all(widget.get_active_text())
                rows = self.sqlUtils.convert_tuple_to_list(data)
                
                count = 0
                for row in rows:
                    self.model.append(row)
                    count +=1
                    
                self.labelRows.set_text(str(count))        
                
                self.END_TIME = datetime.now()
                self.DIFERENCE_TIME =  get_time_difference(self.START_TIME, self.END_TIME)
                
                
                self.boxTreeView.show_all()
                self.labelTime.set_text(self.DIFERENCE_TIME)
            except sqlite3.OperationalError as error:
                pass
            finally:
                self.meta.disconnect()
            
    """Metodo para filtrar el treeview cuando se introduce texto en el campo buscar"""
    def on_action_changed_search_treeview(self, widget):
        self.modelFilter.refilter()    
        
    """Metodo para obtener el numero del item del combobox seleccionado"""
    def on_action_column_entry_changed(self, widget):
        self.numberColumn = widget.get_value_as_int()
    
    """Metodo para comparar el texto que queremos filtrsr en el treeview"""
    def match_func(self, model, iterr,data=None):
        try:                
            text = self.entrySearchTreeView.get_text()
            value = model.get_value(iterr, self.numberColumn)

            if text == "":
                return True
            elif text in value.lower():
                return True
            return False
        except TypeError as error:
            pass

    """Metodo para validar un numero entero en el campo ir a fila"""
    def on_action_go_to_entry_validation(self, widget, text, size, position):
        text = text[:size]
        if text.isnumeric() == False:
            widget.emit_stop_by_name("insert_text")
            return True
        else:
            return False    
                     
    """Metodo que selecciona la fila que el indiquemos en el campo de ir a fila"""        
    def on_action_go_to_entry(self, widget):
        if self.treeview is not None:
            column = self.treeview.get_column(0)
            n = self.entryGoToTreeView.get_text()
            n = int(n)
            self.treeview.set_cursor(n-1, column, True)       
    
    """Metodo que no hace nada solo nos srive para invokar que el combobox se active"""    
    def on_action_popdown_combobox(self, widget):
        pass    
   
    """Metodo que sirve para volver a cargar los datos""" 
    def on_action_button_refresh_clicked(self, widget):
        self.comboxTables.remove_all()
        self.init_gui()
    
        for child in self.boxTreeView.get_children():
            child.destroy()
        
        self.entrySearchTreeView.set_text("")
        self.entryColumnTreeView.set_value(0)
        self.entryGoToTreeView.set_text("")
        self.labelColumns.set_text("Empty")
        self.labelRows.set_text("Empty")
        self.labelTime.set_text("Empty")
     
        
    """Metodo para añadir las combinaciones de teclas para los widgets"""        
    def add_accelerator_widget(self, widget, accelerator, signal="activate"):
        if accelerator is not None:
            key, mod = Gtk.accelerator_parse(accelerator)
            widget.add_accelerator(signal, self.myAccelerators, key, mod, Gtk.AccelFlags.VISIBLE)
            
            
     
