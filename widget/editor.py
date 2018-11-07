# editor.py
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

import gi, os, sqlite3, sqlparse, time
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, GtkSource, GObject, Gio, Pango
from datetime import datetime, time as datetime_time, timedelta
from widget.connection import SQLMeta, SQLUtils, Connection
from widget.notebook import DynamicNotebook
from widget.source import SourceText, LogView
from widget.dialog import OpenSQLFileDialog, SaveSQLFileDialog
from widget.file import File
from widget.resource import *
from widget.method import *


"""Clase para ejecutar pequeñas querys"""

class EditorView(Gtk.Box):
    def __init__(self, CURRENT_DATABASE, myAccelerators, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        """Asignando las variables globales"""        
        self.CURRENT_DATABASE = CURRENT_DATABASE
        self.myAccelerators = myAccelerators    
        self.parent = parent


        """Declarando variables para acceder a la information de la base de  datos"""                                 
        self.sqlUtils = SQLUtils()           
        self.meta = SQLMeta()
        
        """Declarando variables auxiliares"""         
        self.CURRENT_SQL = None
        
        """"Obteniendo los objetos de la ui"""          
        builder = Gtk.Builder()
        builder.add_from_file(UI_EDITOR)
        self.boxRoot = builder.get_object("boxRoot")        
        self.boxNotebookEditor = builder.get_object("boxNotebookEditor")        
        self.buttonNewTabEditor = builder.get_object("buttonNewTabEditor")
        self.buttonOpenFileTabEditor = builder.get_object("buttonOpenFileTabEditor")
        self.buttonSaveTabEditor = builder.get_object("buttonSaveTabEditor")
        self.buttonSaveAsTabEditor = builder.get_object("buttonSaveAsTabEditor")
        self.buttonFormatTabEditor = builder.get_object("buttonFormatTabEditor")
        self.formatCapitalizeItem = builder.get_object("formatCapitalizeItem")
        self.formatLowerItem = builder.get_object("formatLowerItem")
        self.formatUpperItem = builder.get_object("formatUpperItem")     
        self.buttonExecute = builder.get_object("buttonExecute")   
        self.buttonExecuteBuffer = builder.get_object("buttonExecuteBuffer")        
        self.boxNotebookLog = builder.get_object("boxNotebookLog")
        self.buttonClearAllLog = builder.get_object("buttonClearAllLog")        
        
        """Añadiendo iconos a los botones"""        
        set_widget_image(self.buttonNewTabEditor, ICON_TAB_NEW)        
        set_widget_image(self.buttonOpenFileTabEditor, ICON_OPEN)
        set_widget_image(self.buttonSaveTabEditor, ICON_SAVE)
        set_widget_image(self.buttonSaveAsTabEditor, ICON_SAVE_AS)
        set_widget_image(self.buttonExecute, ICON_EXECUTE)
        set_widget_image(self.buttonExecuteBuffer, ICON_BUFFER)
        set_widget_image(self.buttonClearAllLog, ICON_CLEAN)
        self.buttonFormatTabEditor.set_from_file(ICON_FORMAT)
                       
        """Añadiendo combinaciones de teclas para los botones"""
        self.add_accelerator_widget(self.buttonNewTabEditor, "<Alt>N", "clicked")        
        self.add_accelerator_widget(self.buttonOpenFileTabEditor, "<Alt>O", "clicked")    
        self.add_accelerator_widget(self.buttonSaveTabEditor, "<Alt>G", "clicked")             
        self.add_accelerator_widget(self.buttonSaveAsTabEditor, "<Alt>S", "clicked")       
        self.add_accelerator_widget(self.formatCapitalizeItem, "<Alt>C", "activate")                        
        self.add_accelerator_widget(self.formatLowerItem, "<Alt>L", "activate")        
        self.add_accelerator_widget(self.formatUpperItem, "<Alt>U", "activate")  
        self.add_accelerator_widget(self.buttonExecute, "<Alt>comma", "clicked")  
        self.add_accelerator_widget(self.buttonExecuteBuffer, "<Alt>period", "clicked")                                    
        self.add_accelerator_widget(self.buttonClearAllLog, "<Alt>R", "clicked")           
        
        """Añadiendo metodos para los widgets"""                               
        self.buttonNewTabEditor.connect("clicked", self.on_action_add_tab_editor_button)
        self.buttonOpenFileTabEditor.connect("clicked", self.on_action_open_file_tab_editor_button)      
        self.buttonSaveTabEditor.connect("clicked", self.on_action_save_tab_editor_button)
        self.buttonSaveAsTabEditor.connect("clicked", self.on_action_save_as_tab_editor_button)  
        self.formatCapitalizeItem.connect("activate", self.on_action_format_and_capitalize)
        self.formatLowerItem.connect("activate", self.on_action_format_and_lowercase)                        
        self.formatUpperItem.connect("activate", self.on_action_format_and_uppercase)                
        self.buttonExecute.connect("clicked", self.on_action_execute) 
        self.buttonExecuteBuffer.connect("clicked", self.on_action_execute_buffer)             
        self.buttonClearAllLog.connect("clicked", self.on_action_clear_log)
        
        """Cargando la interfaz grafica"""         
        self.init_gui()
        self.pack_start(self.boxRoot, True, True, 0)      
        
    """Metodo para cargar la interfaz"""          
    def init_gui(self):
        self.notebookEditor = DynamicNotebook()
        self.notebookEditor.set_scrollable(True)  
        sourceview = SourceText(self.notebookEditor)
        self.notebookEditor.append_page(sourceview, Gtk.Label("untitled"))      
        self.boxNotebookEditor.pack_start(self.notebookEditor, True, True, 0)
        
        self.notebookLog = DynamicNotebook()
        self.notebookLog.set_scrollable(True)
        self.logger = LogView()
        
        labelLog = Gtk.Label("Log")
        labelLog.modify_font(Pango.FontDescription.from_string("Sans bold 10"))
        self.notebookLog.append_page_fixed(self.logger, labelLog)            
        self.boxNotebookLog.pack_start(self.notebookLog, True, True, 0)
                 
    """Metodo para guardar como un archivo de texto abierto"""               
    def init_save_as_file_to_editor(self):
        dialog = SaveSQLFileDialog(self.parent)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.CURRENT_SQL = dialog.file_name()
            
            f = File()
            widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())
            widget.set_tooltip_text("{0}".format(self.CURRENT_SQL))
            sourceview = widget.get_children()
            _buffer = sourceview[0].get_buffer()
            f.save_as_sql_file_from_editor(self.CURRENT_SQL, _buffer)
            widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())           
            path, filename = os.path.split(self.CURRENT_SQL)
            self.notebookEditor.set_path_title(filename)
        elif response == Gtk.ResponseType.CANCEL:
            print("Canceled")

        dialog.destroy()    
    
    """Metodo para auxiliar para ejecutar las querys del editor"""
    def insert_result(self, sql):
        self.meta.connect(self.CURRENT_DATABASE)
        try:     
            widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())
            editorText = widget.get_tooltip_text()           
            path, editor = os.path.split(editorText)   
            if(sqlparse.parse(sql)[0].get_type() in ['CREATE','DELETE','INSERT','DROP','UPDATE', 'ALTER']):                    
                START_TIME = datetime.now()                 
                self.meta.get_data_from_query(sql, True)                
                END_TIME = datetime.now()
                DIFERENCE_TIME = get_time_difference(START_TIME, END_TIME)
                count = len(self.logger.get_model())+1
                sql = sql.replace('\n', ' ').replace('\r', '')                
                self.logger.get_model().append([str(count), sql, "✔️","Success", DIFERENCE_TIME, editor])                
            else:
                START_TIME = datetime.now()
                data, cursor = self.meta.get_data_from_query(sql)
    
                columns = [description[0] for description in cursor.description]
                columnsCount = len(columns)
                
                scroll = Gtk.ScrolledWindow()
                treeview = Gtk.TreeView()
                treeview.columns_autosize()
                treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
                scroll.add(treeview)

                labelCountRowsPage3 = Gtk.Label()
                labelCountRowsPage3.set_xalign(0.00)

                boxResults = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                boxResults.pack_start(scroll, True, True, 0)
                boxResults.pack_start(labelCountRowsPage3, False, False, 0)
                
                self.notebookLog.append_page_logger(boxResults, Gtk.Label("Result"))
                        
                model = Gtk.ListStore(*[str]* columnsCount)
                treeview.set_model(model)

                count = 0
                for i in columns:
                    column = Gtk.TreeViewColumn(i, Gtk.CellRendererText(), text=count)
                    count +=1
                    treeview.append_column(column)

                temporal = self.sqlUtils.convert_tuple_to_list(data)                
                for i in temporal:                    
                    model.append(i)
                END_TIME = datetime.now()
                DIFERENCE_TIME = get_time_difference(START_TIME, END_TIME)                
                rows = len(temporal)
                labelCountRowsPage3.modify_font(Pango.FontDescription.from_string("Sans 8"))
                labelCountRowsPage3.set_markup(" <b>Columns: </b><i>{0}</i>\t<b>Rows: </b><i>{1}</i>\t<b>Time: </b><i>{2}</i>\t<b>From: </b><i>{3}</i>".format(columnsCount,rows,DIFERENCE_TIME,editor))
                count = len(self.logger.get_model())+1
                sql = sql.replace('\n', ' ').replace('\r', '')                 
                self.logger.get_model().append([str(count), sql, "✔️","Success", DIFERENCE_TIME, editor]) 
        except sqlite3.OperationalError as error:
            count = len(self.logger.get_model())+1
            sql = sql.replace('\n', ' ').replace('\r', '') 
            self.logger.get_model().append([str(count), sql, "❌",str(error), "", editor])
        except sqlite3.IntegrityError as error:
            count = len(self.logger.get_model())+1        
            sql = sql.replace('\n', ' ').replace('\r', '') 
            self.logger.get_model().append([str(count), sql, "❌",str(error), "",editor])            
        except TypeError as error:
            pass        
        
        self.meta.disconnect()        

    """Metodo para agregar una tab al notebook"""
    def on_action_add_tab_editor_button(self, widget):
        sourceview = SourceText(self.notebookEditor)
        self.notebookEditor.append_page(sourceview, Gtk.Label("untitled"))  
        self.notebookEditor.show_all()
        
    """Metodo para abrir un archivo en el editor"""
    def on_action_open_file_tab_editor_button(self, widget):
        dialog = OpenSQLFileDialog(self.parent)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            try:
                if(os.path.isfile(dialog.file_name())):
                    self.CURRENT_SQL = dialog.file_name()

                    if(self.notebookEditor.get_n_pages() == 0):
                        sourceview = SourceText(self.notebookEditor)
                        self.notebookEditor.append_page(sourceview, Gtk.Label("untitled"))                      
                        self.notebookEditor.show_all()

                        widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())
                        widget.set_tooltip_text("{0}".format(self.CURRENT_SQL))
                        sourceview = widget.get_children()
                        _buffer = sourceview[0].get_buffer()

                        f = File()                        
                        f.open_sql_file_to_editor(self.CURRENT_SQL, _buffer)
   
                                        
                        path, filename = os.path.split(self.CURRENT_SQL)
                        self.notebookEditor.set_tab_label(widget, Gtk.Label(filename)) 
                        #self.notebookEditor.set_path_title(filename)
                        dialog.destroy()
                    else:
                        widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())
                        widget.set_tooltip_text("{0}".format(self.CURRENT_SQL))
                        sourceview = widget.get_children()
                        _buffer = sourceview[0].get_buffer()
                        
                        f = File()
                        f.open_sql_file_to_editor(self.CURRENT_SQL, _buffer)
                        
                        path, filename = os.path.split(self.CURRENT_SQL)
                        self.notebookEditor.set_tab_label(widget, Gtk.Label(filename)) 
                        #self.notebookEditor.set_path_title(filename)
                        dialog.destroy()
                else:
                    dialog.destroy()
                    msg = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error dir is not a valid file")
                    msg.format_secondary_text("Please select a valid sql file")
                    msg.run()
                    msg.destroy()       
            except UnicodeDecodeError as error:
                dialog.destroy()
                msg = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error can't open file'")
                msg.format_secondary_text("The file encoding could not be decoded")
                msg.run()
                msg.destroy()       
        
    """Metodo para guardar el texto la tab seleccionada"""       
    def on_action_save_tab_editor_button(self, widget):
        if self.CURRENT_SQL != None and self.notebookEditor.get_n_pages() > 0:
            file = File()            
            widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())
            sourceview = widget.get_children()
            _buffer = sourceview[0].get_buffer()
            full_path = widget.get_tooltip_text()        
            path, filename = os.path.split(full_path)
            
            
            self.notebookEditor.set_tab_label(widget, Gtk.Label(filename))               
            f = File()
            f.save_sql_file_from_editor(full_path, _buffer)          
        else:
            self.init_save_as_file_to_editor()
        
    def on_action_save_as_tab_editor_button(self, widget):
        if(self.notebookEditor.get_n_pages() > 0):
            self.init_save_as_file_to_editor()
        
    """Metodo para formatear y capitalizar las palabra reservadas"""                
    def on_action_format_and_capitalize(self, widget):
        widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())
        sourceview = widget.get_children()
        _buffer = sourceview[0].get_buffer()
        
        startIter = _buffer.get_start_iter()
        endIter = _buffer.get_end_iter()
        text = _buffer.get_text(startIter,endIter, True)
        
        _buffer.delete(startIter, endIter)

        formated_text = self.sqlUtils.format_capitalize(text)
        _buffer.set_text(formated_text)

    """Metodo para formatear y pasar a minusculas las palabra reservadas"""        
    def on_action_format_and_lowercase(self, widget):
        widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())
        sourceview = widget.get_children()
        _buffer = sourceview[0].get_buffer()
        
        startIter = _buffer.get_start_iter()
        endIter = _buffer.get_end_iter()
        text = _buffer.get_text(startIter,endIter, True)
        
        _buffer.delete(startIter, endIter)

        formated_text = self.sqlUtils.format_lower(text)
        _buffer.set_text(formated_text)
        
    """Metodo para formatear y pasar a mayusculas las palabra reservadas"""
    def on_action_format_and_uppercase(self, widget):
        widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())
        sourceview = widget.get_children()
        _buffer = sourceview[0].get_buffer()
        
        startIter = _buffer.get_start_iter()
        endIter = _buffer.get_end_iter()
        text = _buffer.get_text(startIter,endIter, True)
        
        _buffer.delete(startIter, endIter)

        formated_text = self.sqlUtils.format_upper(text)
        _buffer.set_text(formated_text)
   
    """Metodo para ejecutar todo el texto que se encuentre en el editor"""
    def on_action_execute(self, widget):
        try: 
            self.logger.get_model().clear()
            tabs = self.notebookLog.get_n_pages()
            while(tabs != 0):
                self.notebookLog.remove_page(tabs)
                tabs -=1            
            
            widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())
            editorText = widget.get_tooltip_text()
            
            currentSource = widget.get_children()
            _buffer = currentSource[0].get_buffer()
            startIter = _buffer.get_start_iter()
            endIter = _buffer.get_end_iter() 
            text = _buffer.get_text(startIter, endIter, True)  
            text = text.rstrip('\n')                
            
            sqlStatements = sqlparse.split(text)
            
            statements = []        
            for i in sqlStatements:
                formatedText = sqlparse.format(i, reindent=True,keyword_case='upper', strip_comments=True)
                statements.append(formatedText)
            
            statements = list(filter(None, statements)) # fastest

            if len(statements) >= 1:  
                n = len(statements)
                for i in range(0,n):
                    self.insert_result(statements[i])                           
        except sqlite3.OperationalError as error:
            print(error)
        except AttributeError as error:
            print(error)
        finally:
            self.boxNotebookLog.show_all()
                  
                        
    """Metodo para executar el texto que se encuentra en el buffer"""   
    def on_action_execute_buffer(self, widget):
        try:           
            widget = self.notebookEditor.get_nth_page(self.notebookEditor.get_current_page())
            editorText = widget.get_tooltip_text()
            currentSource = widget.get_children()
            _buffer = currentSource[0].get_buffer()
            startIter, endIter = _buffer.get_selection_bounds()
            text = _buffer.get_text(startIter, endIter, True)
            text = text.rstrip('\n')                
            currentSource = widget.get_children()
            _buffer = currentSource[0].get_buffer()

            sqlStatements = sqlparse.split(text)
            
            statements = []        
            for i in sqlStatements:
                formated_text = sqlparse.format(i, reindent=True,keyword_case='upper', strip_comments=True)
                statements.append(formated_text)
            
            statements = list(filter(None, statements)) # fastest

            if len(statements) >= 1:   
                self.notebookLog.set_current_page(0)
                n = len(statements)
                for i in range(0,n):
                    self.insert_result(statements[i])
        except sqlite3.OperationalError as error:
            print(error)
        except AttributeError as error:
            print(error)
        except ValueError as error:
            pass            
        finally:
            self.boxNotebookLog.show_all()
            
            
    """Metodo para limpiar el logger"""  
    def on_action_clear_log(self, widget):
        tabs = self.notebookLog.get_n_pages()
        while(tabs != 0):
            self.notebookLog.remove_page(tabs)
            tabs -=1
            
        self.logger.get_model().clear()   
        
                    
    """Metodo para añadir las combinaciones de teclas para los widgets"""            
    def add_accelerator_widget(self, widget, accelerator, signal="activate"):
        if accelerator is not None:
            key, mod = Gtk.accelerator_parse(accelerator)
            widget.add_accelerator(signal, self.myAccelerators, key, mod, Gtk.AccelFlags.VISIBLE)
            
        
