# -*- coding: utf-8 -*-

##############################################################################
#
#  版权所有 (c) , 2013 , IntoStudio 
#
##############################################################################

import logging

from osv import osv
from openerp.osv import osv
_logger = logging.getLogger(__name__)


class ir_model(osv.osv):
    """
    修改 ir_model 的 name_get,

    """
    _inherit = 'ir.model'
    # _rec_name = 'model'
    #
    #
    #     'name': fields.char('Model Description', size=64, translate=True, required=True),
    #     'model': fields.char('Model', size=64, required=True, select=1),

    def name_get(self, cr, uid, ids, context=None):
        """返回显示 name 和 model 两个字段"""
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        res = [(r['id'], r['model'] and '%s [%s]' % (r['name'], r['model']) or r['name'])
               for r in self.read(cr, uid, ids, ['name', 'model'], context=context)]
        return res

