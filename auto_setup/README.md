    本模块在Openerp创建数据库的时候 自动安装,目前做了三件事
    1. 调整 Settings 菜单下面 Modules 下面的几个菜单的顺序,
       把 Installed Modules 提前,
       删除 apps 和  update 菜单
    2. 把 admin 加到 Technical Features 组
    3. 自动安装好 指定模块
    4. 模块是 我自己需要的 安装状态, 使用前 请根据 注释 适度修改一下.


    开发这个模块的缘由是在 学习过程中,经常需要新建数据库, 上面三个步骤几乎是每次都要做的.

    本模块 不需要特意安装, 在新建数据库的时候会自动安装, 并完成上述工作

    2013.06.12 00:13
    by ccdos@intoerp.com