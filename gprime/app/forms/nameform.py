#
# gPrime - a web-based genealogy program
#
# Copyright (c) 2015 Gramps Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from .forms import Form

class NameForm(Form):
    """
    A form for listing, viewing, and editing user settings.
    """
    table = "Person"
    def __init__(self, database, _, instance, handle, row):
        super().__init__(database, _, instance)
        self.tview = self._("Name")
        self.view = "Name"
        self.row = row
        self.handle = handle

    def save(self):
        pass
        # save the settings to the user table

