# -*- coding: utf-8 -*-
##############################################################################
#
#    auto select smtp server for Openerp
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
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Charset import Charset
from email.Header import Header
from email.Utils import formatdate, make_msgid, COMMASPACE

from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.tools import html2text
import openerp.tools as tools

from openerp.addons.base.ir.ir_mail_server import  extract_rfc2822_addresses

class ir_mail_server(osv.osv):
    """发送邮件之前, 根据 smtp_from 查找对应的 smtp 服务器, 如果找不到对应,保留原状."""
    _inherit = "ir.mail_server"
    _columns = {
    }

    def send_email(self, cr, uid, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False,
                   context=None):

        smtp_from = message['Return-Path'] or message['From']
        assert smtp_from, "The Return-Path or From header is required for any outbound email"

        # The email's "Envelope From" (Return-Path), and all recipient addresses must only contain ASCII characters.
        from_rfc2822 = extract_rfc2822_addresses(smtp_from)
        assert len(from_rfc2822) == 1, "Malformed 'Return-Path' or 'From' address - it may only contain plain ASCII characters"
        smtp_from = from_rfc2822[0]

        #################################################
        # patch: 首先查找 smtp_from 对应的 smtp 服务器
        # 要求 定义 Outgoing Mail Servers 时候, 确保 Description(name) 字段的值 为对应的 邮件发送账户(完整的eMail地址)
        # 本模块以此 为 邮件的发送者 查找 smtp 服务器
        # 需要为系统中 每个可能发送邮件的账户 按以上要求设置一个 服务器

        mail_server_ids = self.search(cr, SUPERUSER_ID, [('name','=',smtp_from)], order='sequence', limit=1)
        if mail_server_ids:
            mail_server = self.browse(cr, SUPERUSER_ID, mail_server_ids[0])
            mail_server_id = mail_server_ids[0]

        res = super(ir_mail_server,self).send_email(cr, uid,
                                                    message,
                                                    mail_server_id,
                                                    smtp_server,
                                                    smtp_port,
                                                    smtp_user,
                                                    smtp_password,
                                                    smtp_encryption,
                                                    smtp_debug,
                                                    context)
        return res