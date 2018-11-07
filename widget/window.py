# window.py
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

"""Importando los modulos necesarios """

import gi, os, sqlite3
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, Gio, GObject, GtkSource, GdkPixbuf
from pathlib import Path
from widget.homepage import HomePage
from widget.structure import StructureView
from widget.browser import BrowserView
from widget.editor import EditorView
from widget.resource import *
from widget.dialog import *


"""Clase principal de la aplicacion"""

class CattusWindow(Gtk.Application):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, application_id='org.application.cattus', flags=Gio.ApplicationFlags.FLAGS_NONE, **kwargs)
        pass
        
    """Metodo para declarar los widgets y las variables"""
    def do_startup(self):
        Gtk.Application.do_startup(self)
        GObject.type_register(GtkSource.View)
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_WINDOW)

        """Obteniendo los objetos de la ui"""        
        self.headerbar = self.builder.get_object("headerbar")
        self.window = self.builder.get_object("cattusWindow")        
        self.rootBox = self.builder.get_object("rootBox")
        
        """Declarando las variables globales"""
        self.CURRENT_DATABASE = None
        self.stackSidebar = None
        self.stack = None
                
    """"Metodo para inicializar los widgets y las variables"""
    def do_activate(self):
        Gtk.Application.do_activate(self)
        self.window.set_icon(GdkPixbuf.Pixbuf.new_from_file(ICON_CATTUS_ICON))
        
        """Cargando el menu para la aplicacion"""
        self.set_app_menu(self.init_menu()) 
        
        
        """Agregando la pantalla por defecto"""
        self.rootBox.pack_start(HomePage(), True, True, 0)                
        self.window.set_application(self)
        self.window.present()
        
        """Declarando una variable para guardar las combinaciones de teclas para los widgets"""
        self.myAccelerators = Gtk.AccelGroup()
        self.get_window_by_id(1).add_accel_group(self.myAccelerators)
                
        self.window.show_all()
            
    """Metodo para la contruccion del menu de la aplicacion"""
    def init_menu(self):
        menu = Gio.Menu()
        menu.append("Open Database", "app.open")
        menu.append("New Database", "app.new")
        menu.append("about", "app.about")                        
        menu.append("Exit", "app.quit")

        action = Gio.SimpleAction.new("open", None)
        action.connect("activate", self.on_action_open)
        self.add_action(action)
        self.add_accelerator("<Control>O", "app.open")
                        
        action = Gio.SimpleAction.new("new", None)
        action.connect("activate", self.on_new)
        self.add_action(action)
        self.add_accelerator("<Control>N", "app.new")                        
                                
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)
        self.add_accelerator("<Control>I", "app.about")                

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit, self)
        self.add_action(action)
        self.add_accelerator("<Control>Q", "app.quit")

        return menu

    """Metodo para abrir la base de datos"""
    def on_action_open(self, action, param):
        if self.CURRENT_DATABASE is None:
            self.init_open() 
        else:
            message = create_question_message(self.get_window_by_id(1), "There is already an open database","¿Do you want to close it?")
            option = message.run()
            if option == Gtk.ResponseType.OK:
                self.init_open()
            message.destroy()                

    
    """Metodo auxiliar para abrir la base de datos"""
    def init_open(self):
        dialog = OpenDBDialog(self.get_window_by_id(1))
        response = dialog.run()    
        if response == Gtk.ResponseType.OK:
            if(os.path.isfile(dialog.file_name()) and Path(dialog.file_name()).suffix == ".db"):
                self.CURRENT_DATABASE = dialog.file_name()
                dialog.destroy()
                    
                path, database = os.path.split(self.CURRENT_DATABASE)
                self.headerbar.set_title(database)
                self.headerbar.set_subtitle(path)
                
                
                """Quitar cerrar base de datos del menu de la aplicacion"""    
                menu = self.get_app_menu()        
                if menu.get_n_items() == 6:
                    menu.remove(2)
                    
                """Volver a agregar cerrar base de datos al menu de la aplicacion"""
                menu = self.get_app_menu()        
                menu.insert(2,"Close Database", "app.close")
                action = Gio.SimpleAction.new("close", None)
                action.connect("activate", self.on_close)
                self.add_action(action)
                self.add_accelerator("<Control>W", "app.close")       
                     
                  
                """Quitamos la pantalla por defecto de la aplicacion"""  
                for child in self.rootBox.get_children():
                    child.destroy()
                        
                        
                """Agregamos la interfaz principal de la aplicacion"""
                self.stack = Gtk.Stack()    
                self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
                self.stackSidebar = Gtk.StackSidebar()
                self.stackSidebar.set_stack(self.stack)                        
                    
                self.structure = StructureView(self.CURRENT_DATABASE, self.myAccelerators,self.get_window_by_id(1))
                self.stack.add_titled(self.structure, "page0", "Structure")
                
                self.browser = BrowserView(self.CURRENT_DATABASE, self.myAccelerators)
                self.stack.add_titled(self.browser, "page1", "Browser")
                    
                self.editorSQL = EditorView(self.CURRENT_DATABASE, self.myAccelerators, self.get_window_by_id(1))
                self.stack.add_titled(self.editorSQL, "page2", "Editor")                        
                    
                self.rootBox.pack_start(self.stackSidebar, False, True, 0)
                self.rootBox.pack_start(self.stack, True, True, 0)            
                self.rootBox.show_all()                    
            
                dialog.destroy()            
            else:
                dialog.destroy()
                msg = Gtk.MessageDialog(self.get_window_by_id(1), 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error of selection")
                msg.format_secondary_text("Selected item is not a valid file")
                msg.run()
                msg.destroy()
                                       


    def on_new(self, action, param):
        dialog = NewDBDialog(self.get_window_by_id(1))
        option = dialog.run()
        if option == Gtk.ResponseType.OK:
            database = open(dialog.file_name(), 'w')
            database.close()
            
            self.CURRENT_DATABASE = dialog.file_name()
            path, database = os.path.split(self.CURRENT_DATABASE)
            self.headerbar.set_title(database)
            self.headerbar.set_subtitle(path)
                
            menu = self.get_app_menu()        
            if menu.get_n_items() == 6:
                menu.remove(2)
                
                
            menu = self.get_app_menu()        
            menu.insert(2,"Close Database", "app.close")
            action = Gio.SimpleAction.new("close", None)
            action.connect("activate", self.on_close)
            self.add_action(action)
            self.add_accelerator("<Control>W", "app.close")            
                
            for child in self.rootBox.get_children():
                child.destroy()
                    
            self.stack = Gtk.Stack()    
            self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
            self.stackSidebar = Gtk.StackSidebar()
            self.stackSidebar.set_stack(self.stack)        
                
            self.structure = StructureView(self.CURRENT_DATABASE, self.myAccelerators,self.get_window_by_id(1))
            self.stack.add_titled(self.structure, "page0", "Structure")
                
            self.browser = BrowserView(self.CURRENT_DATABASE, self.myAccelerators)
            self.stack.add_titled(self.browser, "page1", "Browser")
                
            self.editorSQL = EditorView(self.CURRENT_DATABASE, self.myAccelerators, self.get_window_by_id(1))
            self.stack.add_titled(self.editorSQL, "page2", "Editor")                        
                
            self.rootBox.pack_start(self.stackSidebar, False, True, 0)
            self.rootBox.pack_start(self.stack, True, True, 0)            
            self.rootBox.show_all()
            dialog.destroy()    

        dialog.destroy()

    def on_close(self, action, param):
        if self.CURRENT_DATABASE is not None:
            for child in self.rootBox.get_children():
                child.destroy()
                
            """Quitar cerrar base de datos del menu de la aplicacion"""    
            menu = self.get_app_menu()        
            menu.remove(2)
            
            self.CURRENT_DATABASE = None
            self.headerbar.set_title("")
            self.headerbar.set_subtitle("")
            self.rootBox.pack_start(HomePage(), True, True, 0)        
            self.rootBox.show_all()

        
    def on_about(self, action, param):
        dialog = AboutDialog(self.get_window_by_id(1))
        dialog.run()
        dialog.destroy()   
            
    def on_quit(self, action, param, app): 
        app.quit()
                             
          

