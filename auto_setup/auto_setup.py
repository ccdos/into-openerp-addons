# -*- coding: utf-8 -*-
##############################################################################
#
#    auto setup for Openerp
#    Copyright (C) 2013 ccdos (<http://www.intoerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class module(osv.osv):
    """

    """
    _inherit = "ir.module.module"
    _columns = {
        }
    def install_module(self, cr, uid, name_list, context=None):

        to_install_ids = []
        for module_name in name_list:
            module_ids = self.search(cr, uid,
                [('name', '=', module_name)], {})
            print module_name
            if len(module_ids) != 1 :
                raise osv.except_osv(u'指定的模块名称 %s 不是唯一的' % module_name )

            # self.button_install(cr, uid, module_ids, {})
            to_install_ids.append(module_ids[0])

        if to_install_ids:
            self.button_install(cr, uid, to_install_ids, context=context)


