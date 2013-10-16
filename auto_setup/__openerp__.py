# -*- coding: utf-8 -*-
 

{
    'name': 'auto_setup',
    'version': '1.0',
    'category': 'Base',
    'description': """

    本模块在Openerp创建数据库的时候 自动安装,目前做了三件事
    1. 调整 Settings 菜单下面 Modules 下面的几个菜单的顺序,
       主要是把 apps 移到后面, 把 Installed Modules 提前
    2. 把 admin 加到 Technical Features 组
    3. 自动安装好 指定模块

    开发这个模块的缘由是在 学习过程中,经常需要新建数据库, 上面三个步骤几乎是每次都要做的.

    """,
    'author': 'CCDOS',
    'website': 'http://www.intoerp.com',
    'depends': ['base'],
    'data': [
       'auto_setup.xml',
    ],
    'css': [
        'static/src/css/auto_setup.css'
    ],
    'qweb' : [
        "static/src/xml/base.xml",
    ],
    'installable': True,
    'auto_install': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
