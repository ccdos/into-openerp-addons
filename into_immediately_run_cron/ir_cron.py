# -*- coding: utf-8 -*-
##############################################################################

import logging

from openerp.osv import osv

_logger = logging.getLogger(__name__)


class ir_cron(osv.osv):
    _inherit = "ir.cron"

    def Immediately_run_cron(self, cr, uid, ids, context=None):
        jobs = self.browse(cr, uid, ids, context=context)
        for job in jobs:
            self._callback(cr, job.user_id.id, job.model, job.function, job.args, job.id)
