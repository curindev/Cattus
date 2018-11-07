# homepage.py
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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from widget.resource import ICON_WELCOME



"""Clase para mostrar la pantalla por defecto"""

class HomePage(Gtk.Alignment):
    def __init__(self):
        super().__init__()
        self.set_padding(50,50,50,50)             
        self.image = Gtk.Image()
        self.image.set_from_file(ICON_WELCOME)
        self.image.set_tooltip_markup("Open database <b>(Ctrl+O)</b> ")
        self.add(self.image)
        self.show_all()

