# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 南京 ccdos ccdos@intoerp.com).
#
##############################################################################
from osv import fields, osv
from datetime import time, datetime
from openerp.tools.translate import _
from ast import literal_eval
from dateutil.relativedelta import relativedelta


class sale_order(osv.osv):
    _inherit = "sale.order"


    def check_validity(self, cr, uid, ids):
        """ 检查 订单 是否允许被 安排生产
        @return: True or False    默认直接允许生成，如果 需要完整实现，继承此方法扩展实现，示例见后面的备注
        """
        # raise osv.except_osv(_('批准订单时!'), _('存在 C 类商品，必须由生产副总进行批准!') )
        return True        

    # def check_validity(self, cr, uid, ids):
        # """ 检查 订单 是否允许被 安排生产
        # @return: True or False
        # """
        # for record in self.browse(cr, uid, ids):
            # today_date = datetime.today().strftime('%Y-%m-%d')
            # if 不符合要求 就抛错:
                # raise osv.except_osv(_('批准订单时!'), _('存在 C 类商品，必须由生产副总进行批准!') )
        # return True   