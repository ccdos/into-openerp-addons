# -*- coding: utf-8 -*-
 

{
    'name': 'User Role',
    'version': '1.0',
    'category': 'Base',
    'description': """

用户角色

定义角色，每个角色可以指派 若干个组，

将用户指定 若干角色后，自动将 这些角色 具备的 用户组权限 指派给 该用户。

本模块的意义在与，快速给用户授权

功能：

1. 建立角色，指派 访问权限（todo：功能模仿 用户 的访问权限）

2. 从某个用户复制 其访问权限

3. 用户 跟 角色 为 m2m 关系

4. 保存时 ，将角色的 访问权限 指派给对应的用户

5. 为避免误操作，禁止admin被加入任何角色

    """,
    'author': 'CCDOS',
    'website': 'http://www.intoerp.com',
    'depends': ['base'],
    'data': [
        'res_user_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
