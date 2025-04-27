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
from web.controllers.main import ExcelExport





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

    def parse_domain(self, domain):
        """
        解析复杂的 domain 表达式，特别是包含时间表达式的 domain
        
        :param domain: 原始 domain 列表
        :return: 解析后的 domain 列表
        """
        # 导入需要的模块
        from openerp.tools.safe_eval import safe_eval
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        import time

        parsed_domain = []
        if not domain:
            return parsed_domain

        try:
            # 如果 domain 是字符串列表，需要逐个解析
            if isinstance(domain, list):
                for dom in domain:
                    if isinstance(dom, basestring):
                        # 准备解析环境
                        eval_context = {
                            # 返回 datetime 对象而不是字符串
                            'context_today': lambda: datetime.now(),
                            'datetime': datetime,
                            'relativedelta': relativedelta,
                            'time': time,
                            'str': str,  # 添加 str 函数以便于转换
                        }
                        # 将字符串形式的 domain 转换为 Python 对象
                        try:
                            dom_eval = safe_eval(dom, eval_context)
                            if isinstance(dom_eval, list):
                                parsed_domain.extend(dom_eval)
                            else:
                                parsed_domain.append(dom_eval)
                        except Exception as e:
                            print("Error parsing domain string:", dom, e)
                            # 如果解析失败，尝试直接使用
                            parsed_domain.append(dom)
                    else:
                        # 如果不是字符串，直接添加
                        parsed_domain.append(dom)
            else:
                parsed_domain = domain

            print("Original domain:", domain)
            print("Parsed domain:", parsed_domain)
        except Exception as e:
            print("Error parsing domain:", e)
            parsed_domain = domain

        return parsed_domain

    @openerpweb.httprequest
    def index(self, req, data, token):
        data = json.loads(data)
        model = data.get('model', '')
        ids = data.get('ids', [])
        fields = data.get('fields', [])
        headers = data.get('headers', [])
        domain = data.get('domain', [])
        context = data.get('context', {})
        sort = data.get('sort', '')
        total_records = data.get('total_records', 0)  # 获取前端传递的总记录数

        print("Received record IDs:", len(ids), "Domain:", domain)
        print("Context:", context)
        print("Sort:", sort)
        print("Total records from frontend:", total_records)

        # 使用解析方法处理 domain
        parsed_domain = self.parse_domain(domain)
        
        # 获取数据库连接
        Model = req.session.model(model)

        # 合并上下文
        user_context = req.context.copy()
        if context:
            user_context.update(context)

        # 准备排序参数
        order = sort or False

        # 使用解析后的 domain 获取数据
        records = []
        # 使用 search_read 方法一次性获取所有符合条件的记录
        result = Model.search_read(parsed_domain, fields, 0, False, order, user_context)
        records = result.get('records', []) if isinstance(result, dict) and 'records' in result else result
        print("Using search_read, found", len(records), "records")

        # 准备导出数据
        rows = []
        for record in records:
            row = []
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

                row.append(value)
            rows.append(row)

        print(u'total rows:', len(rows))
        if total_records <> len(rows):
            # 前后端记录数不同, 输出错误信息
            print("Error: Total records mismatch: expected %d, got %d" % (total_records, len(rows)))

            

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
