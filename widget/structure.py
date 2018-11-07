# structure.py
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
from widget.connection import SQLMeta, SQLUtils
from widget.dialog import ExportDialog, RemoveDialog
from widget.resource import *
from widget.method import *

"""Clase para mostrar la estructura de la base de datos"""
class StructureView(Gtk.Box):
    def __init__(self, CURRENT_DATABASE, myAccelerators, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL) 

        """Asignando las variables globales"""
        self.CURRENT_DATABASE = CURRENT_DATABASE
        self.myAccelerators = myAccelerators
        self.parent = parent
        
        """Declarando variables para acceder a la information de la base de datos"""
        self.meta = SQLMeta()
        self.sqlUtils = SQLUtils()        
        
        """"Obteniendo los objetos de la ui"""
        builder = Gtk.Builder()
        builder.add_from_file(UI_STRUCTURE)        
        self.boxRoot = builder.get_object("boxRoot")
        self.treeviewStructure = builder.get_object("treeviewStructure")
        self.sourceviewScheme = builder.get_object("sourceviewScheme")
        self.buttonRefresh = builder.get_object("buttonRefresh")
        self.buttonExport = builder.get_object("buttonExport")  
        self.buttonRemove = builder.get_object("buttonRemove")       
                
        """Añadiendo iconos a los botones"""
        set_widget_image(self.buttonRefresh, ICON_REFRESH)
        set_widget_image(self.buttonExport, ICON_EXPORT)
        set_widget_image(self.buttonRemove, ICON_CLEAN)

        """Añadiendo propiedades a los widgets"""
        set_treeview_configuration(self.treeviewStructure)
        set_sourceview_configuration(self.sourceviewScheme)                             
        
        """Añadiendo combinaciones de teclas para los botones"""
        self.add_accelerator_widget(self.buttonRefresh, "<Alt>R", signal="clicked")
        self.add_accelerator_widget(self.buttonExport, "<Alt>E", signal="clicked")   
        self.add_accelerator_widget(self.buttonRemove, "<Alt>R", signal="clicked")        
                
        """Añadiendo metodos para los widgets"""
        self.buttonRefresh.connect("clicked", self.on_action_refresh)        
        self.buttonExport.connect("clicked", self.on_action_export)
        self.buttonRemove.connect("clicked", self.on_action_remove)
        
        """Cargando la interfaz grafica"""                 
        self.init_gui()
        self.pack_start(self.boxRoot, True, True, 0)    
        
        
    """Metodo para cargar la interfaz"""
    def init_gui(self):    
        """Creando el modelo para la tabla que va a mostrar la estructura"""
        self.treeStore = Gtk.TreeStore(str,str,str,str,str)    
        columns = ["NAME", "TYPE", "NOT NULL", "PRIMARY KEY", "TYPE"]
        for i in range(0,len(columns)):
            column = Gtk.TreeViewColumn(columns[i], Gtk.CellRendererText(), text=i)
            self.treeviewStructure.append_column(column)        
        self.treeviewStructure.set_model(self.treeStore)
        
        """Creando una señal de seleccion para el treeview"""
        select = self.treeviewStructure.get_selection()
        select.connect("changed", self.on_activate_row)
        
        """Llamando a la funcion para llenar la tabla"""
        self.fill_treeview_structure()
     
        
    """Metodo para volver a cargar la ui"""
    def on_action_refresh(self, widget):
        self.treeStore.clear()
        self.fill_treeview_structure()
                
    """Metodo para llamar al dialogo de exportacion de tablas"""
    def on_action_export(self, widget):
        dialog = ExportDialog(self.parent, self.CURRENT_DATABASE)
        dialog.run()
        dialog.destroy()
                
    """Metodo para llamar al dialog de eliminacion de tablas"""
    def on_action_remove(self, widget):
        dialog = RemoveDialog(self.parent, self.CURRENT_DATABASE)
        dialog.run()
        dialog.destroy()      
        
    """Metodo para extraer el sql scheme de una tabla seleccionada del treeview"""
    def on_activate_row(self, selection):
        model, treeiter = selection.get_selected()        
        node = None
        type_d = None
        if treeiter is not None:
            node = model[treeiter][0]
            type_d = model[treeiter][4]
        try:  
            self.item = node[1:len(node)]
        except TypeError as error:
            pass
        self.meta.connect(self.CURRENT_DATABASE)
        scheme = self.meta.get_name_scheme_from_master(self.item, type_d)
        
        BUFFER = self.sourceviewScheme.get_buffer()
        START_ITER = BUFFER.get_start_iter()
        END_ITER = BUFFER.get_end_iter()
        
        BUFFER.delete(START_ITER, END_ITER)
        
        try:
            text = self.sqlUtils.convert_tuple_to_list(scheme)
            BUFFER.insert(END_ITER, text[0][1], -1)
            
        except IndexError as error:
            pass
        except TypeError as error:
            pass    
        
        self.meta.disconnect()
        
    """Metodo para llenar el treeview"""
    def fill_treeview_structure(self):
        self.meta.connect(self.CURRENT_DATABASE)
        
        numberTables = self.meta.get_count_type('table')
        if len(numberTables) > 0:
            self.node = self.treeStore.append(None,["▦Tables({0})".format(numberTables[0]), "","","",""])
            tables = self.meta.get_name_from_master('table')
            for table in self.sqlUtils.convert_tuple_to_list(tables):
                self.table = self.treeStore.append(self.node, ["▦"+table[0], "", "", "", "table"])
                
                tables_info = self.meta.get_table_info(table[0])
                for info in self.sqlUtils.convert_tuple_to_list(tables_info):
                    self.treeStore.append(self.table,[info[1], info[2].upper(), self.sqlUtils.is_nn(info[3]), self.sqlUtils.is_pk(info[5]),  "" ])
                        
        numberIndices = self.meta.get_count_type('index')
        if len(numberIndices) > 0:
            self.node = self.treeStore.append(None, ["▦Indices({0})".format(numberIndices[0]), "", "", "", ""])
            indices = self.meta.get_name_from_master('index')
            for indice in self.sqlUtils.convert_tuple_to_list(indices):
                self.treeStore.append(self.node,["▦"+indice[0], "", "", "", "index"])
                
        numberViews = self.meta.get_count_type('view')
        if len(numberViews) > 0:
            self.node = self.treeStore.append(None, ["▦Views({0})".format(numberViews[0]), "", "", "", ""])
            views = self.meta.get_name_from_master('view')
            for view in self.sqlUtils.convert_tuple_to_list(views):
                self.treeStore.append(self.node,["▦"+view[0], "", "", "", "view"])            
        
        self.meta.disconnect()    
        
        
    """Metodo para añadir las combinaciones de teclas para los widgets"""
    def add_accelerator_widget(self, widget, accelerator, signal="activate"):
        if accelerator is not None:
            key, mod = Gtk.accelerator_parse(accelerator)
            widget.add_accelerator(signal, self.myAccelerators, key, mod, Gtk.AccelFlags.VISIBLE)
            
            

