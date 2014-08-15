# -*- coding: utf-8 -*-

##############################################################################
#
#  版权所有 (c) , 2013 , IntoStudio 
#
##############################################################################

from osv import osv, fields
import math
import re

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class product_product(osv.osv):
    """
    产品模版表增加一个字段, 
    """
    _inherit = "product.product"
    _columns = {
        'list_price_uos': fields.float('Uos Sale Price', digits_compute=dp.get_precision('Product Price'), 
            help="基本销售单位的 价格"),
        }

    def write(self, cr, uid, ids, vals, context=None):
        uos_coeff = False
        if vals.has_key("list_price_uos") :
            list_price_uos = vals["list_price_uos"]
            if vals.has_key("uos_coeff") :
                uos_coeff = vals["uos_coeff"]

            if  (not uos_coeff) :
                product_obj = self.pool.get('product.product')
                product = product_obj.browse(cr, uid, ids,context=context)[0]
                #print product.uos_id
                uos_coeff = product.uos_coeff

            if uos_coeff and list_price_uos:
                vals["list_price"] =  list_price_uos  * uos_coeff

        return super(product_product, self).write(cr, uid, ids, vals, context)

    def create(self, cr, uid, vals, context=None):
        uos_coeff = False
        if vals.has_key("list_price_uos") :
            list_price_uos = vals["list_price_uos"]
            if vals.has_key("uos_coeff") :
                uos_coeff = vals["uos_coeff"]
                if uos_coeff and list_price_uos:
                    vals["list_price"] =  list_price_uos  * uos_coeff

        # print 'create vals:%s' % vals
        return super(product_product, self).create(cr, uid, vals, context)



class sale_order_line(osv.osv):
    """
    添加字段：price_unit_uos
    暂无 计算逻辑
    """
    _inherit = 'sale.order.line'
    _columns = {
        'price_unit_uos': fields.float('Uos Unit Price', required=False, digits_compute= dp.get_precision('Product Price'), readonly=True, states={'draft': [('readonly', False)]}),
        }
    _defaults = {
        'price_unit_uos':0,
        }

    # def write(self, cr, uid, ids, vals, context=None):
    #     # warning_msgs = {}
    #     # print 'write vals:%s' % vals
    #     return super(sale_order_line, self).write(cr, uid, ids, vals, context)
    #
    # def create(self, cr, uid, vals, context=None):
    #     # warning_msgs = {}
    #     # print 'create vals:%s' % vals
    #     return super(sale_order_line, self).create(cr, uid, vals, context)