# dialog.py
#
# Copyright 2018 Jose Francisco
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

"""Importando los modulos necesarios"""

import gi, sqlite3
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from widget.connection import SQLMeta, SQLUtils
from widget.file import File
from widget.resource import *

"""Metodo para crear un mensaje"""
def create_question_message(parent, head=None, body=None):
    message = Gtk.MessageDialog(parent, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, head)
    message.format_secondary_text(body)
    return message
            


class ExportDialog():
    def __init__(self, parent,CURRENT_DATABASE):
        self.parent = parent
        self.CURRENT_DATABASE = CURRENT_DATABASE

        self.meta = SQLMeta()
        self.sqlUtils = SQLUtils()
        self.file = File()
                
        builder = Gtk.Builder()
        builder.add_from_file(UI_EXPORT)
        self.dialog = builder.get_object("dialog")
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(self.parent)
        
        self.statusBarMessage = builder.get_object("statusBarMessage")
        self.statusBarMessage.connect("response", self.on_action_close_message)        
        self.labelMessage = builder.get_object("labelMessage")
        
        self.stack = builder.get_object("stack")
        
        self.treeview = builder.get_object("treeview")
        self.model = Gtk.ListStore(str, bool)
        self.treeview.set_model(self.model)
        
        columnTable = Gtk.TreeViewColumn("Table", Gtk.CellRendererText(), text=0)
        rendererToggle = Gtk.CellRendererToggle()
        rendererToggle.connect("toggled", self.on_action_toggled_cell_export)
        columnExport = Gtk.TreeViewColumn("Export", rendererToggle, active=1)
        
        self.treeview.append_column(columnTable)
        self.treeview.append_column(columnExport)
        
        self.meta.connect(self.CURRENT_DATABASE)
        data = self.meta.get_name_from_master('table')
        for i in self.sqlUtils.convert_tuple_to_list(data):
            self.model.append([i[0], False])
        self.meta.disconnect()
        
        self.checkExportXlsx = builder.get_object("checkExportXlsx")
        self.checkExportCsv = builder.get_object("checkExportCsv")
        
        self.checkExportSql = builder.get_object("checkExportSql")
        self.checkExportSql.connect("toggled", self.on_action_export_sql)
        self.boxSqlOption = builder.get_object("boxSqlOption")
        self.oneFile = builder.get_object("oneFile")
        
        self.buttonFileChooser = builder.get_object("buttonFileChooser")
        
        self.buttonExport = builder.get_object("buttonExport")
        self.buttonExport.connect("clicked", self.on_action_export_button)
        self.buttonExportImage = Gtk.Image()
        self.buttonExportImage.set_from_file(ICON_EXPORT)
        self.buttonExport.set_image(self.buttonExportImage)         
        
        self.imageExportOK = builder.get_object("imageExportOK")
        self.imageExportOK.set_from_file(ICON_OPERATION_OK)
        
        self.buttonCloseDialog = builder.get_object("buttonCloseDialog")
        self.buttonCloseDialog.connect("clicked", self.on_action_dialog_destroy)
        
    def on_action_export_sql(self, widget):
        if self.checkExportSql.get_active() == True:            
            self.boxSqlOption.set_visible(True)
        else:
            self.boxSqlOption.set_visible(False)
        
    def on_action_close_message(self, widget, response_id):
        self.statusBarMessage.set_property("revealed", False)        
        
    def on_action_toggled_cell_export(self, widget, path):
        self.model[path][1] = not self.model[path][1]
        
    def on_action_export_button(self, widget):
        if self.buttonFileChooser.get_filename() is not None:
            path = self.buttonFileChooser.get_filename()
            if not os.path.exists(path): os.makedirs(path)
            
            count = 0
            for row in self.model:
                if row[1] == True:
                    count +=1
            
            status = False
            
            if count == 0:
                self.labelMessage.set_text("Error no table selected")
                self.statusBarMessage.set_property("revealed", True)  
            else:                        
                if self.checkExportXlsx.get_active():
                    for row in self.model:
                        if row[1] == True:       
                            self.meta.connect(self.CURRENT_DATABASE)
                            self.cursor = self.meta.CURSOR
                            data = self.meta.get_select_all(row[0])
                            columns = [description[0] for description in self.cursor.description]
                            rows = self.sqlUtils.convert_tuple_to_list(data)       
                            self.file.save_xlsx_file(path, row[0], columns, rows)
                            self.meta.disconnect()
                            status =True
                if self.checkExportCsv.get_active():
                    for row in self.model:
                        if row[1] == True:
                            self.meta.connect(self.CURRENT_DATABASE)
                            self.cursor = self.meta.CURSOR
                            data = self.meta.get_select_all(row[0])
                            columns = [description[0] for description in self.cursor.description]
                            rows = self.sqlUtils.convert_tuple_to_list(data)       
                            self.file.save_csv_file(path, row[0], columns, rows)
                            self.meta.disconnect()       
                            status =True
                            
                if self.checkExportSql.get_active():
                    script = ""
                    if self.oneFile.get_active():
                        for row in self.model:
                            if row[1] == True:                            
                                self.meta.connect(self.CURRENT_DATABASE)              
                                self.cursor1 = self.meta.CURSOR
                                self.cursor2 = self.meta.CURSOR
                                
                                data = self.meta.get_scheme_from_master(row[0], "table")

                                    
                                scheme = self.sqlUtils.convert_tuple_to_list(data)
                                data2 = self.cursor2.execute("SELECT * FROM {0}".format(row[0]))
                                    
                                columns = [description[0] for description in self.cursor2.description]
                                rows = self.sqlUtils.convert_tuple_to_list(data2)       
                                    
                                script += self.file.generate_scrip(row[0], scheme, columns, rows)  
                                
                                ruta, filename =os.path.split(self.CURRENT_DATABASE)
                                f = os.path.join(path,filename[0:len(filename)-3]+".sql")
                                self.file.save_sql_script_one_file(f, script)
                                
                                self.meta.disconnect()
                                status = True
                                
                    else:
                        for row in self.model:
                            script = ""
                            if row[1] == True:                            
                                self.meta.connect(self.CURRENT_DATABASE)              
                                self.cursor1 = self.meta.CURSOR
                                self.cursor2 = self.meta.CURSOR
                                
                                data = self.meta.get_scheme_from_master(row[0], "table")

                                    
                                scheme = self.sqlUtils.convert_tuple_to_list(data)
                                data2 = self.cursor2.execute("SELECT * FROM {0}".format(row[0]))
                                    
                                columns = [description[0] for description in self.cursor2.description]
                                rows = self.sqlUtils.convert_tuple_to_list(data2)       
                                    
                                script += self.file.generate_scrip(row[0], scheme, columns, rows)
                                self.file.save_sql_script_file(path, row[0]+".sql", script)
                                self.meta.disconnect()                                  
                                status = True
                                                         
                                                            
                if self.checkExportXlsx.get_active() == False and self.checkExportCsv.get_active() == False and self.checkExportSql.get_active() == False:
                    status =False
                    self.labelMessage.set_text("Please select an export option")
                    self.statusBarMessage.set_property("revealed", True)  
                    
                    
                if status == True:
                    self.statusBarMessage.set_property("revealed", False)        
                    self.dialog.set_title("The tables were exported sucessfully")
                    self.stack.set_visible_child_name("page1")
        else:
            self.labelMessage.set_text("Please select a destination directory")
            self.statusBarMessage.set_property("revealed", True)  
              
            	
    def on_action_dialog_destroy(self, widget):
        self.dialog.destroy()
        
    def filter_db(self):
        self.filter = Gtk.FileFilter()
        self.filter.set_name("folder")
        self.filter.add_mime_type("inode/directory")
        self.dialog.add_filter(self.filter)    
        
    def file_name(self):
        return self.dialog.get_filename()
    
    def run(self):
        return self.dialog.run()
        
    def destroy(self):
        return self.dialog.destroy()   


class RemoveDialog():
    def __init__(self, parent,CURRENT_DATABASE):        
        self.parent = parent
        self.CURRENT_DATABASE = CURRENT_DATABASE
        
        self.meta = SQLMeta()
        self.sqlUtils = SQLUtils()
        self.file = File()
                
        builder = Gtk.Builder()
        builder.add_from_file(UI_REMOVE)
        self.dialog = builder.get_object("dialog")
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(self.parent)
        
        self.statusBarMessage = builder.get_object("statusBarMessage")
        self.statusBarMessage.connect("response", self.on_action_close_message)        
        self.labelMessage = builder.get_object("labelMessage")        
        
        self.stack = builder.get_object("stack")
        
        self.treeview = builder.get_object("treeview")
        self.model = Gtk.ListStore(str, str,bool)
        self.treeview.set_model(self.model)                        
        
        columnName = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0)
        columnType = Gtk.TreeViewColumn("Type", Gtk.CellRendererText(), text=1)
        rendererToggle = Gtk.CellRendererToggle()
        rendererToggle.connect("toggled", self.on_action_toggled_cell_export)
        columnExport = Gtk.TreeViewColumn("Remove", rendererToggle, active=2)
        
        self.treeview.append_column(columnName)        
        self.treeview.append_column(columnType)
        self.treeview.append_column(columnExport)
        
        
        self.imageDeleteOK = builder.get_object("imageDeleteOK")
        self.imageDeleteOK.set_from_file(ICON_OPERATION_OK)
        self.buttonCloseDialog = builder.get_object("buttonCloseDialog")
        
        self.meta.connect(self.CURRENT_DATABASE)
        data = self.meta.get_name_from_master('table')
        for i in self.sqlUtils.convert_tuple_to_list(data):
            self.model.append([i[0], "table",False])        
                        
        data = self.meta.get_name_from_master('index')
        for i in self.sqlUtils.convert_tuple_to_list(data):
            self.model.append([i[0], "index",False])
        
        data = self.meta.get_name_from_master('view')
        for i in self.sqlUtils.convert_tuple_to_list(data):
            self.model.append([i[0], "view",False])
        self.meta.disconnect()
                
        self.buttonExport = builder.get_object("buttonRemove")
        self.buttonExport.connect("clicked", self.on_action_remove_button)
        self.buttonCloseDialog.connect("clicked", self.on_action_dialog_destroy)
        
        self.buttonExportImage = Gtk.Image()
        self.buttonExportImage.set_from_file(ICON_CLEAN)
        self.buttonExport.set_image(self.buttonExportImage)                         
        
    def on_action_dialog_destroy(self, widget):
        self.dialog.destroy()
    
    def on_action_close_message(self, widget, response_id):
        self.statusBarMessage.set_property("revealed", False)        
        
    def on_action_toggled_cell_export(self, widget, path):
        self.model[path][2] = not self.model[path][2]
        
    def on_action_remove_button(self, widget):
        count = 0
        for row in self.model:
            if row[2] == True:
                count +=1
                                
        if count == 0:
            self.labelMessage.set_text("Error there are no selected items")
            self.statusBarMessage.set_property("revealed", True)  
        else:
            deleteOK = False
            self.meta.connect(self.CURRENT_DATABASE)                
            for row in self.model:
                if row[1] == "table" and row[2] ==True:
                    try:
                        self.meta.remove_from_master("table", row[0])
                        deleteOK = True
                    except sqlite3.IntegrityError as error:
                        self.labelMessage.set_text(str(error))
                        self.statusBarMessage.set_property("revealed", True)  
                        deleteOK = False                        
                elif row[1] == "index" and row[2] ==True:
                    self.meta.remove_from_master("index", row[0])                    
                    deleteOK = True
                elif row[1] == "view" and row[2] ==True:
                    self.meta.remove_from_master("view", row[0])                                    
                    deleteOK = True
            
            self.meta.disconnect()
            if deleteOK:
                self.stack.set_visible_child_name("page1")

    def run(self):
        return self.dialog.run()
        
    def destroy(self):
        return self.dialog.destroy()   


class SaveSQLFileDialog():
    def __init__(self, parent):
        self.dialog = Gtk.FileChooserDialog("Please choose a sql file", parent,Gtk.FileChooserAction.SAVE,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.dialog.set_modal(True)
        self.dialog.set_do_overwrite_confirmation(True)
        self.filter_db()
        
    def filter_db(self):
        self.filter = Gtk.FileFilter()
        self.filter.set_name("SQlite files")
        self.filter.add_mime_type("application/sql")
        self.dialog.add_filter(self.filter)    
        
    def file_name(self):
        return self.dialog.get_filename()
    
    def run(self):
        return self.dialog.run()
        
    def destroy(self):
        return self.dialog.destroy()   


class OpenSQLFileDialog():
    def __init__(self, parent):
        self.dialog = Gtk.FileChooserDialog("Please choose a sql file", parent,Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.dialog.set_modal(True)
        self.filter_db()
        
    def filter_db(self):
        self.filter = Gtk.FileFilter()
        self.filter.set_name("SQlite files")
        self.filter.add_mime_type("application/sql")
        self.dialog.add_filter(self.filter)    
        
    def file_name(self):
        return self.dialog.get_filename()
    
    def run(self):
        return self.dialog.run()
        
    def destroy(self):
        return self.dialog.destroy()   

class OpenDBDialog():
    def __init__(self, parent):
        self.dialog = Gtk.FileChooserDialog("Please choose a DataBase", parent,Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.dialog.set_modal(True)
        self.filter_db()
        
    def filter_db(self):
        self.filter = Gtk.FileFilter()
        self.filter.set_name("SQlite files")
        self.filter.add_mime_type("application/x-sqlite3")
        self.filter.add_mime_type("text/plain")
        self.dialog.add_filter(self.filter)    
        
    def file_name(self):
        return self.dialog.get_filename()
    
    def run(self):
        return self.dialog.run()
        
    def destroy(self):
        return self.dialog.destroy()    
    

class NewDBDialog():
    def __init__(self, parent):
        self.dialog = Gtk.FileChooserDialog("Please set database name", parent,Gtk.FileChooserAction.SAVE,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.dialog.set_modal(True)
        self.filter_db()
        
    def filter_db(self):
        self.filter = Gtk.FileFilter()
        self.filter.set_name("SQlite files")
        self.filter.add_mime_type("application/x-sqlite3")
        self.dialog.add_filter(self.filter)    
        
    def file_name(self):
        return self.dialog.get_filename()
    
    def run(self):
        return self.dialog.run()
        
    def destroy(self):
        return self.dialog.destroy()    
        
    
    
class ThirdPartiesDialog():
    def __init__(self, parent):
        builder = Gtk.Builder()
        builder.add_from_file(UI_PARTIES)
        
        self.dialog = builder.get_object("dialog")
        self.dialog.set_transient_for(parent)
        
        self.labelSqlParseVersion = builder.get_object("labelSqlParseVersion")
        self.labelSqlParseVersion.set_markup("<b>sqlparse:</b> <i>{0}</i>".format(sqlparse.__version__))        
        
        self.labelXlsxwriter = builder.get_object("labelXlsxwriter")
        self.labelXlsxwriter.set_markup("<b>xlsxwriter:</b> <i>{0}</i>".format(xlsxwriter.__version__))
        
        self.labelSqliteVersion = builder.get_object("labelSqliteVersion")
        self.labelSqliteVersion.set_markup("<b>sqlite:</b> <i>{0}</i>".format(sqlite3.sqlite_version))
        
        self.labelPythonVersion = builder.get_object("labelPythonVersion")
        version = "{0}.{1}.{2}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
        self.labelPythonVersion.set_markup("<b>python:</b> <i>{0}</i>".format(version))
                
        
    def run(self):
        self.dialog.run()
        
    def destroy(self):
        self.dialog.destroy()   
                
class AboutDialog():
    def __init__(self, parent):
        logo = GdkPixbuf.Pixbuf.new_from_file(ICON_CATTUS)
        builder = Gtk.Builder()
        builder.add_from_file(UI_ABOUT)
        
        self.dialog = builder.get_object("dialog")
        self.dialog.set_logo(logo)
        self.dialog.set_transient_for(parent)            
        
    def run(self):
        self.dialog.run()
        
    def destroy(self):
        self.dialog.destroy()
        
               
