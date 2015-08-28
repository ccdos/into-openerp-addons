# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 南京 ccdos ccdos@intoerp.com).
#
##############################################################################
from osv import fields, osv
from openerp import netsvc

class sale_order(osv.osv):
    _inherit = "sale.order"

    _columns = {
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date_approval', 'Waiting Approval'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
        ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
    }
    def action_cancel_draft(self, cr, uid, ids, context=None):
        if not len(ids):
            return False
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for p_id in ids:
            # Deleting the existing instance of workflow for PO
            wf_service.trg_delete(uid, 'sale.order', p_id, cr)
            wf_service.trg_create(uid, 'sale.order', p_id, cr)
        return True

    def test_need_approval(self, cr, uid, ids):
        """
        @return: True or False
        检查 订单是否满足批准的条件 由 不同的  由 不同的  Signal 触发， 这样的 同样的 源activity  和 目的 activity，
        可以有多个 不同的 transition，

        使用场景示例： 需要审批的订单（返回 True）， 必须由  总经理/副总经理 进行批准
                      否则（返回False）， 由 生产计划员可以直接批准

        实际项目使用，应该 重写此方法 根据实际需要 返回相应的 值
        """
        res = False

        return res

    def check_validity(self, cr, uid, ids):
        """ 检查 订单 是否允许被 安排生产
        @return: True or False    默认直接允许生成，如果 需要完整实现，继承此方法扩展实现，示例见后面的备注
        """
        # raise osv.except_osv(_('批准订单时!'), _('存在 C 类商品，必须由生产副总进行批准!') )
        return True        
