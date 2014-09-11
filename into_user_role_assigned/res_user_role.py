# -*- coding: utf-8 -*-

##############################################################################
#
#  版权所有 (c) , 2013 , IntoStudio 
#
##############################################################################

from osv import osv, fields
import math
import re

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)
from openerp import SUPERUSER_ID

class user_role(osv.osv):
    """
    user_role,

    """
    _name = 'res.users.role'
    _description = u"用户角色"
    _columns = {
        'name':fields.char(u'角色名称', size=64),
        'user_ids':fields.many2many('res.users', 'user_role_rel', 'role_id', 'user_id', string=u'用户', help=u"具有本角色的用户"),
        'groups_id': fields.many2many('res.groups', 'res_groups_users_role_rel', 'uid', 'gid', u'用户组'),
    }

    def write(self, cr, uid, ids, vals, context=None):

        assert len(ids) == 1, " 用户角色每次只允许写入一条记录"

        # 阻止 admin 用户被加入任何角色
        if vals.has_key('user_ids') \
            and  vals['user_ids'][0] \
            and vals['user_ids'][0][0] == 6 \
            and SUPERUSER_ID in vals['user_ids'][0][2] :
                raise osv.except_osv(u'建立角色时!', u' 禁止admin 用户被加入任何角色！')

        # 首先读入 角色原来的 的权限 到 o_groups_id
        old_role = self.read(cr, uid, ids,['user_ids','groups_id'], context)

        o_groups_id = old_role[0]['groups_id']

        result = super(user_role, self).write(cr, uid, ids, vals, context)
#         if vals
# SUPERUSER_ID

        # 读入 角色修改后的权限
        role = self.read(cr, uid, ids,['user_ids','groups_id'], context)
        user_ids =  role[0]['user_ids']
        groups_id = role[0]['groups_id']

        # 对新 旧权限进行比较，分为 添加和删除两个部分
        v  =  [(4,item) for item in groups_id if item  not in o_groups_id]    # 存在于新权限，不在 旧权限，属于添加   （4，id） 添加记录
        v +=  [(3,item) for item in o_groups_id  if item  not in groups_id]  # 存在于旧权限，不在新权限， 属于删除部分 （3，id） 删除记录
        for u in user_ids:
            self.pool.get('res.users').write(cr, uid, [u], { 'groups_id': v }, context ) # 逐一对用户 写入（删除权限）

        return result

    def create(self, cr, uid, vals, context=None):

        # 阻止 admin 用户被加入任何角色
        if vals.has_key('user_ids') \
            and  vals['user_ids'][0] \
            and vals['user_ids'][0][0] == 6 \
            and SUPERUSER_ID in vals['user_ids'][0][2] :
                raise osv.except_osv(u'建立角色时!', u' 禁止admin 用户被加入任何角色！')


        result = super(user_role, self).create(cr, uid, vals, context)

        # 下面将刚刚定义的角色的权限，逐一写入 每个用户，因为是新建的，不存在 删除权限的情况，因此直接 添加权限
        role = self.browse(cr, uid, result, context)
        for u in  role.user_ids:
            self.pool.get('res.users').write(cr, uid, [u.id], { 'groups_id':  [ (4,g.id) for g in  role.groups_id]    }, context )

        return result


    def get_user_access_right(self, cr, uid, ids, context=None):
        """
        读取现有用户的权限

        reduce
        """

        role = self.read(cr, uid, ids,['user_ids','groups_id'], context)

        for r in role:
            for u in r['user_ids']:
                print u
                user = self.pool.get('res.users').read(cr, uid, u,['groups_id'], context)
                v  =  [(4,item) for item in user['groups_id'] ]

                # super(user_role, self).write(cr, uid, [r['id']], { 'groups_id': v }, context )  # 这样的调用会保证不会立即对每个用户进行权限写入， 但是会导致
                self.write(cr, uid, [r['id']], { 'groups_id': v }, context )  # 此行写入会触发对每个用户写入相同的权限

        return True


class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'role_ids':fields.many2many('res.users.role', 'user_role_rel', 'user_id', 'role_id', string=u'角色', help=u"本用户具备的橘色"),
    }
    def write(self, cr, uid, ids, vals, context=None):
        # warning_msgs = {}
        print 'write res_users vals:%s' % vals
        result = super(res_users, self).write(cr, uid, ids, vals, context)

        return result

    def create(self, cr, uid, vals, context=None):
        # warning_msgs = {}
        print 'create res_users vals:%s' % vals
        result = super(res_users, self).create(cr, uid, vals, context)
        return result
res_users()
