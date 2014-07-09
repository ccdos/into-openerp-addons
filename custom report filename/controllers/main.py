# -*- coding: utf-8 -*-

import time
import simplejson
import openerp.addons.web.http as openerpweb
from openerp.addons.web.controllers.main import Reports
import urllib
import openerp
import openerp.modules.registry
from openerp.tools.translate import _
from openerp.tools import config

class CustFileNameReports(Reports):
    _cp_path = "/web/report"

    @openerpweb.httprequest
    def index(self, req, action, token):
        action = simplejson.loads(action)

        report_srv = req.session.proxy("report")
        context = dict(req.context)
        context.update(action["context"])

        report_data = {}
        report_ids = context["active_ids"]

        try:
            if  action['attachment']:
                model = context['active_model']
                cr = openerp.pooler.get_db(req.session._db).cursor()
                uid = context['uid']
                ids = context['active_ids']
                objects=openerp.pooler.get_pool(req.session._db).get(model).browse(cr,uid,ids,context=context)
                file_name=[eval(action['attachment'],{'object':x, 'time':time}) for x in objects][0]
                action['name'] = file_name
        except:
            pass

        action = simplejson.dumps(action)
        result = super(CustFileNameReports, self).index(req, action, token)
        return result

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
