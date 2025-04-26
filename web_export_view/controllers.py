# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
try:
    import json
except ImportError:
    import simplejson as json

import web.http as openerpweb
from openerp.osv import expression
from openerp.tools.safe_eval import safe_eval
from web.controllers.main import ExcelExport


def string_to_domain_list(domain_string):
    """
    将Odoo domain字符串转换为domain列表，保持函数调用表达式的原始形式

    :param domain_string: Odoo域的字符串表示
    :return: 可用于Odoo搜索的域列表，函数调用会被保留为表达式
    """

    # 移除可能存在的Unicode前缀u
    if domain_string.startswith('u'):
        domain_string = domain_string[1:]

    # 检查和移除字符串的引号
    if (domain_string.startswith('"') and domain_string.endswith('"')) or \
            (domain_string.startswith("'") and domain_string.endswith("'")):
        domain_string = domain_string[1:-1]

    # 使用eval来执行转换，但要小心安全问题
    # 在生产环境中使用时请确保domain_string来源可信
    try:
        # 安全检查：确保字符串符合预期格式
        if not (domain_string.startswith('[') and domain_string.endswith(']')):
            raise ValueError(u"域字符串必须以 '[' 开始并以 ']' 结束")

        # 使用eval直接执行转换
        domain_list = eval(domain_string)

        # 验证结果是否为列表
        if not isinstance(domain_list, list):
            raise ValueError(u"转换结果不是有效的列表")

        return domain_list
    except Exception as e:
        raise ValueError(u"转换域字符串时出错: {str(e)}")


class ExcelExportView(ExcelExport):
    _cp_path = '/web/export/xls_view'

    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)

    @openerpweb.httprequest
    def index(self, req, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        columns_headers = data.get('headers', [])
        rows = data.get('rows', [])

        return req.make_response(
            self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )


class ExcelExportViewAll(ExcelExport):
    _cp_path = '/web/export/xls_view_all'

    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportViewAll, self).__getattribute__(name)

    def _eval_domain(self, req, domain):
        """使用OpenERP原生方法处理domain表达式
        
        处理包含context_today()等函数的domain表达式
        """
        if not domain:
            return []

        # 如果是字符串形式的domain，尝试解析
        if isinstance(domain, list) and len(domain) == 1 and isinstance(domain[0], basestring):
            try:
                # 创建评估上下文
                import datetime
                from dateutil.relativedelta import relativedelta
                from openerp.osv import fields

                # 获取用户上下文
                user_context = req.context.copy() if req.context else {}

                # 创建一个简化的评估上下文
                # 在web控制器中我们没有直接的数据库连接
                # 所以我们使用简化的方式处理context_today

                # 返回datetime对象而不是字符串，这样可以与relativedelta对象进行操作
                def get_today():
                    return datetime.datetime.now()

                eval_context = {
                    'context_today': get_today,
                    'datetime': datetime,
                    'relativedelta': relativedelta,
                    'context': user_context,
                    'uid': req.session._uid if hasattr(req.session, '_uid') else None,
                    'user': req.session._uid if hasattr(req.session, '_uid') else None,
                    # 添加strftime函数供表达式使用
                    'strftime': lambda dt, fmt: dt.strftime(fmt) if hasattr(dt, 'strftime') else str(dt),
                }

                # 使用safe_eval评估domain表达式
                domain = safe_eval(domain[0], eval_context)
            except Exception as e:
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning("Error evaluating domain expression: %s", e)
                return []

        # 使用OpenERP原生的normalize_domain方法处理domain
        try:
            return expression.normalize_domain(domain)
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning("Error normalizing domain: %s", e)
            return domain

    @openerpweb.httprequest
    def index(self, req, data, token):
        data = json.loads(data)
        model = data.get('model', '')
        domain = data.get('domain', [])
        fields = data.get('fields', [])
        headers = data.get('headers', [])

        # 使用OpenERP原生方法处理domain
        domain = self._eval_domain(req, domain)

        # 获取数据库连接
        Model = req.session.model(model)

        # 使用OpenERP原生方法处理domain已经在上面完成
        print("Processed domain:", domain)

        # 搜索所有符合条件的记录 ID
        ids = Model.search(domain, 0, False, False, req.context)

        # 读取所有记录的数据
        records = Model.read(ids, fields, req.context)

        # 准备导出数据
        rows = []
        for record in records:
            row = []
            print(record)
            for field in fields:
                value = record.get(field, '')
                # 首先检查是否为False或None，确保这些值被转换为空字符串
                if value is False or value is None:
                    value = u''
                # 处理不同类型的数据，使其更可读
                elif isinstance(value, (int, long, float)):
                    value = unicode(value)
                elif isinstance(value, tuple) and len(value) == 2:
                    # 这可能是一个 many2one 字段，格式为 (id, name)
                    value = value[1] if value[1] else u''
                elif isinstance(value, (list, tuple)):
                    # 其他类型的列表或元组
                    try:
                        value = u', '.join([unicode(v) for v in value])
                    except:
                        value = unicode(value)
                elif isinstance(value, dict):
                    # 尝试将字典转换为可读格式
                    try:
                        value = u', '.join([u'%s: %s' % (k, v) for k, v in value.items()])
                    except:
                        value = unicode(value)
                elif not isinstance(value, basestring):
                    value = unicode(value)

                # 打印处理前后的值，便于调试
                print("Field: %s, Original: %s, Processed: %s" % (field, record.get(field, ''), value))
                row.append(value)
            rows.append(row)

        # 返回 Excel 文件
        return req.make_response(
            self.from_data(headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
