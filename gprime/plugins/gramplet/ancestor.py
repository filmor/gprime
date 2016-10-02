#
# Gprime - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013-2014  Nick Hall
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

"""Ancestors Gramplet"""

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#------------------------------------------------------------------------
#
# Gprime modules
#
#------------------------------------------------------------------------
from gprime.gen.plug import Gramplet
from gprime.gui.listmodel import ListModel, NOSORT
from gprime.gui.editors import EditPerson
from gprime.gen.errors import WindowActiveError
from gprime.gen.display.name import displayer as name_displayer
from gprime.gen.datehandler import get_date
from gprime.gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gprime.gen.config import config

from gprime.gen.const import LOCALE as glocale
_ = glocale.translation.gettext

class Ancestor(Gramplet):
    """
    Gramplet to display ancestors of the active person.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.view = Gtk.TreeView()
        self.view.set_tooltip_column(3)
        titles = [(_('Name'), 0, 230),
                  (_('Birth'), 2, 100),
                  ('', NOSORT, 1),
                  ('', NOSORT, 1), # tooltip
                  ('', NOSORT, 100)] # handle
        self.model = ListModel(self.view, titles, list_mode="tree",
                               event_func=self.cb_double_click)
        return self.view

    def get_has_data(self, active_handle):
        """
        Return True if the gramplet has data, else return False.
        """
        if active_handle:
            person = self.dbstate.db.get_person_from_handle(active_handle)
            family_handle = person.get_main_parents_family_handle()
            if family_handle:
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family and (family.get_father_handle() or
                               family.get_mother_handle()):
                    return True
        return False

    def cb_double_click(self, treeview):
        """
        Handle double click on treeview.
        """
        (model, iter_) = treeview.get_selection().get_selected()
        if not iter_:
            return

        try:
            handle = model.get_value(iter_, 4)
            person = self.dbstate.db.get_person_from_handle(handle)
            EditPerson(self.dbstate, self.uistate, [], person)
        except WindowActiveError:
            pass

    def db_changed(self):
        self.update()

    def active_changed(self, handle):
        self.update()

    def update_has_data(self):
        active_handle = self.get_active('Person')
        if active_handle:
            self.set_has_data(self.get_has_data(active_handle))
        else:
            self.set_has_data(False)

    def main(self):
        active_handle = self.get_active('Person')
        self.model.clear()
        if active_handle:
            self.add_to_tree(1, None, active_handle)
            self.view.expand_all()
            self.set_has_data(self.get_has_data(active_handle))
        else:
            self.set_has_data(False)

    def add_to_tree(self, depth, parent_id, person_handle):
        """
        Add a person to the tree.
        """
        if depth > config.get('behavior.generation-depth'):
            return

        person = self.dbstate.db.get_person_from_handle(person_handle)
        name = name_displayer.display(person)

        birth = get_birth_or_fallback(self.dbstate.db, person)
        death = get_death_or_fallback(self.dbstate.db, person)

        birth_text = birth_date = birth_sort = ''
        if birth:
            birth_date = get_date(birth)
            birth_sort = '%012d' % birth.get_date_object().get_sort_value()
            birth_text = _('%(abbr)s %(date)s') % \
                         {'abbr': birth.type.get_abbreviation(),
                          'date': birth_date}

        death_date = death_sort = death_text = ''
        if death:
            death_date = get_date(death)
            death_sort = '%012d' % death.get_date_object().get_sort_value()
            death_text = _('%(abbr)s %(date)s') % \
                         {'abbr': death.type.get_abbreviation(),
                          'date': death_date}

        tooltip = name + '\n' + birth_text + '\n' + death_text

        label = _('%(depth)s. %(name)s') % {'depth': depth, 'name': name}
        item_id = self.model.add([label, birth_date, birth_sort,
                                  tooltip, person_handle], node=parent_id)

        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.dbstate.db.get_family_from_handle(family_handle)
            if family:
                father_handle = family.get_father_handle()
                if father_handle:
                    self.add_to_tree(depth + 1, item_id, father_handle)
                mother_handle = family.get_mother_handle()
                if mother_handle:
                    self.add_to_tree(depth + 1, item_id, mother_handle)

        return item_id