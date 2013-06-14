# -*- coding: utf-8 -*-
 

{
    'name': 'uos price',
    'version': '1.0',
    'category': 'Base',
    'description': """
添加一个 基于 uos 的价格字段,
如果输入了 此字段,自动折算出基于 uom 的 list_price

	""",
    'author': 'CCDOS',
    'website': 'http://www.intoerp.com',
    'depends': ['base','product','sale'],
    'data': [
       'uos_price.xml'
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
