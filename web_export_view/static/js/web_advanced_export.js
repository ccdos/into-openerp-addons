//  @@@ web_export_view custom JS @@@
//#############################################################################
//    
//    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
//    Copyright (C) 2012 Therp BV (<http://therp.nl>)
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU Affero General Public License as published
//    by the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU Affero General Public License for more details.
//
//    You should have received a copy of the GNU Affero General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//#############################################################################

openerp.web_export_view = function(instance, m) {

    var _t = instance.web._t,
    QWeb = instance.web.qweb;
    
    // 扩展 ListView 控制器，添加顶部导出按钮
    instance.web.ListView.include({
        init: function(parent, dataset, view_id, options) {
            this._super.apply(this, arguments);
            this.has_export_button = true;  // 启用导出按钮
        },
        
        start: function() {
            var self = this;
            var res = this._super.apply(this, arguments);
            
            // 在视图初始化完成后添加导出按钮
            res.done(function() {
                self.add_export_button();
            });
            
            return res;
        },
        
        add_export_button: function() {
            var self = this;
            // 查找按钮容器
            var $buttons = this.$el.closest('.oe_view_manager').find('.oe_view_manager_buttons');
            if ($buttons.length === 0) {
                return;
            }
            
            // 查找新建/导入按钮所在的容器
            var $button_container = $buttons.find('.oe_list_buttons, .oe_list_add_column, .oe_view_manager_buttons');
            if ($button_container.length === 0) {
                $button_container = $buttons; // 如果找不到特定容器，使用整个按钮区域
            }
            
            // 检查是否已存在导出按钮
            if ($button_container.find('.oe_list_export_button').length > 0) {
                return;
            }
            
            // 创建导出按钮和下拉菜单
            var $export_elements = $(QWeb.render('ListView.ExportButton', {}));
            var $export_button = $export_elements.filter('button');
            var $export_dropdown = $export_elements.filter('ul');
            
            // 添加按钮到与新建/导入按钮相同的容器中
            $button_container.append($export_button);
            // 添加下拉菜单到body，以便正确定位
            $('body').append($export_dropdown);
            
            // 绑定点击事件
            $export_button.on('click', function(e) {
                e.stopPropagation();
                
                // 隐藏所有其他下拉菜单
                $('.oe_dropdown_menu').hide();
                
                // 计算下拉菜单位置
                var button_offset = $export_button.offset();
                var button_height = $export_button.outerHeight();
                
                // 设置下拉菜单位置
                $export_dropdown.css({
                    'top': button_offset.top + button_height + 'px',
                    'left': button_offset.left + 'px'
                });
                
                // 显示/隐藏下拉菜单
                $export_dropdown.toggle();
            });
            
            // 绑定导出当前页事件
            $export_dropdown.find('.oe_list_export_view_xls').on('click', function() {
                self.do_export_view_xls();
                $export_dropdown.hide();
            }).hover(
                function() { $(this).css('background-color', '#f0f0f0'); },
                function() { $(this).css('background-color', ''); }
            );
            
            // 绑定导出全部记录事件
            $export_dropdown.find('.oe_list_export_all_xls').on('click', function() {
                self.do_export_all_xls();
                $export_dropdown.hide();
            }).hover(
                function() { $(this).css('background-color', '#f0f0f0'); },
                function() { $(this).css('background-color', ''); }
            );
            
            // 点击其他地方隐藏下拉菜单
            $(document).on('click', function(e) {
                if (!$(e.target).closest('.oe_list_export_button, .oe_list_export_dropdown').length) {
                    $export_dropdown.hide();
                }
            });
        },
        
        do_export_view_xls: function() {
            // 调用侧边栏的导出当前页方法
            var sidebar = this.sidebar || this.getParent().sidebar;
            if (sidebar && sidebar.on_sidebar_export_view_xls) {
                sidebar.on_sidebar_export_view_xls();
            } else {
                // 如果没有侧边栏，直接实现导出逻辑
                this.export_view_xls();
            }
        },
        
        do_export_all_xls: function() {
            // 调用侧边栏的导出全部记录方法
            var sidebar = this.sidebar || this.getParent().sidebar;
            if (sidebar && sidebar.on_sidebar_export_all_xls) {
                sidebar.on_sidebar_export_all_xls();
            } else {
                // 如果没有侧边栏，直接实现导出逻辑
                this.export_all_xls();
            }
        },
        
        export_view_xls: function() {
            // 实现导出当前页的逻辑，与侧边栏的导出功能类似
            var self = this;
            var export_columns_keys = [];
            var export_columns_names = [];
            
            $.each(this.visible_columns, function(){
                if(this.tag=='field'){
                    export_columns_keys.push(this.id);
                    export_columns_names.push(this.string);
                }
            });
            
            var rows = this.$el.find('.oe_list_content > tbody > tr');
            var export_rows = [];
            
            $.each(rows, function(){
                var $row = $(this);
                if($row.attr('data-id')){
                    var export_row = [];
                    $.each(export_columns_keys, function(){
                        var cell = $row.find('td[data-field="'+this+'"]').get(0);
                        var text = cell.text || cell.textContent || cell.innerHTML || "";
                        if (cell.classList.contains("oe_list_field_float")){
                            export_row.push(instance.web.parse_value(text, {'type': "float"}));
                        }
                        else if (cell.classList.contains("oe_list_field_integer")){
                           export_row.push(parseInt(text));
                        }
                        else{
                           export_row.push(text.trim());
                        }
                    });
                    export_rows.push(export_row);
                }
            });
            
            $.blockUI();
            self.session.get_file({
                url: '/web/export/xls_view',
                data: {data: JSON.stringify({
                    model: self.model,
                    headers: export_columns_names,
                    rows: export_rows,
                })},
                complete: $.unblockUI
            });
        },
        
        export_all_xls: function() {
            // 实现导出全部记录的逻辑，与侧边栏的导出功能类似
            var self = this;
            var export_columns_keys = [];
            var export_columns_names = [];
            
            $.each(this.visible_columns, function(){
                if(this.tag=='field'){
                    export_columns_keys.push(this.id);
                    export_columns_names.push(this.string);
                }
            });
            
            // 获取完整的 domain、context 和 sort 信息
            var domain = [];
            var context = {};
            var sort = '';
            
            try {
                // 创建一个模型对象
                var model = new instance.web.Model(self.model);
                
                // 获取当前的过滤条件
                var filter = [];
                if (self.dataset && self.dataset.domain) {
                    filter = filter.concat(self.dataset.domain);
                }
                
                // 如果有搜索视图，获取搜索视图的过滤条件
                if (self.getParent() && self.getParent().searchview) {
                    var searchview = self.getParent().searchview;
                    var search_data = searchview.build_search_data();
                    if (search_data && search_data.domains) {
                        for (var i = 0; i < search_data.domains.length; i++) {
                            filter = filter.concat(search_data.domains[i]);
                        }
                    }
                }
                
                // 获取当前的上下文
                var ctx = {};
                if (self.dataset && self.dataset.context) {
                    ctx = new instance.web.CompoundContext(ctx, self.dataset.context);
                }
                
                // 使用 model.domain() 获取完整的 domain
                var domain = model.domain(filter);
                
                // 使用 model.context() 获取完整的 context
                var context = model.context(ctx);
                
                // 使用 pyeval.eval 对 domain 和 context 进行解析
                var eval_context = instance.web.pyeval.eval('contexts', [context]);
                var eval_domain = instance.web.pyeval.eval('domains', [domain], eval_context);
                
                // 获取排序信息
                var order_by = self.dataset && self.dataset.sort ? self.dataset.sort : [];
                var sort = instance.web.serialize_sort(order_by);
            } catch (e) {
                console.error("Error getting domain or context:", e);
                var eval_domain = self.dataset ? self.dataset.domain || [] : [];
                var eval_context = self.dataset ? self.dataset.context || {} : {};
                var sort = '';
            }
            
            // 获取当前页面的总记录数
            var total_records = 0;
            if (self.dataset) {
                if (self.dataset._length !== undefined) {
                    total_records = self.dataset._length;
                } else if (self.dataset.ids) {
                    total_records = self.dataset.ids.length;
                }
            }
            
            $.blockUI();
            self.session.get_file({
                url: '/web/export/xls_view_all',
                data: {data: JSON.stringify({
                    model: self.model,
                    ids: self.dataset.ids || [],
                    fields: export_columns_keys,
                    headers: export_columns_names,
                    domain: eval_domain,
                    context: eval_context,
                    sort: sort,
                    total_records: total_records
                })},
                complete: $.unblockUI
            });
        }
    });

    instance.web.Sidebar.include({
        redraw: function() {
            var self = this;
            this._super.apply(this, arguments);
            // 不再显示侧边栏的导出按钮，因为我们已经在顶部添加了导出按钮
        },

        on_sidebar_export_view_xls: function() {
            // Select the first list of the current (form) view
            // or assume the main view is a list view and use that
            var self = this,
            view = this.getParent(),
            children = view.getChildren();
            if (children) {
                children.every(function(child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false; // break out of the loop
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false; // break out of the loop
                    }
                    return true;
                });
            }
            export_columns_keys = [];
            export_columns_names = [];
            $.each(view.visible_columns, function(){
                if(this.tag=='field'){
                    // non-fields like `_group` or buttons
                    export_columns_keys.push(this.id);
                    export_columns_names.push(this.string);
                }
            });
            rows = view.$el.find('.oe_list_content > tbody > tr');
            export_rows = [];
            $.each(rows,function(){
                $row = $(this);
                // find only rows with data
                if($row.attr('data-id')){
                    export_row = [];
                    checked = $row.find('th input[type=checkbox]').attr("checked");
                    if (children && checked === "checked"){
                        $.each(export_columns_keys,function(){
                            cell = $row.find('td[data-field="'+this+'"]').get(0);
                            text = cell.text || cell.textContent || cell.innerHTML || "";
                            if (cell.classList.contains("oe_list_field_float")){
                                export_row.push(instance.web.parse_value(text, {'type': "float"}));
                            }
                            else if (cell.classList.contains("oe_list_field_integer")){
                               export_row.push(parseInt(text));
                            }
                            else{
                               export_row.push(text.trim());
                            }
                        });
                        export_rows.push(export_row);
                    };
                }
            });
            $.blockUI();
            view.session.get_file({
                url: '/web/export/xls_view',
                data: {data: JSON.stringify({
                    model : view.model,
                    headers : export_columns_names,
                    rows : export_rows,
                })},
                complete: $.unblockUI
            });
        },
        
        on_sidebar_export_all_xls: function() {
            // 获取当前视图
            var self = this,
            view = this.getParent(),
            children = view.getChildren();
            if (children) {
                children.every(function(child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false; // break out of the loop
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false; // break out of the loop
                    }
                    return true;
                });
            }
            
            // 获取字段信息
            export_columns_keys = [];
            export_columns_names = [];
            $.each(view.visible_columns, function(){
                if(this.tag=='field'){
                    export_columns_keys.push(this.id);
                    export_columns_names.push(this.string);
                }
            });
            
            // 获取当前视图的 domain、context 和 sort 信息
            $.blockUI();
            
            // 直接使用 model.domain() 和 model.context() 方法获取完整的 domain 和 context
            try {
                // 创建一个模型对象
                var model = new instance.web.Model(view.model);
                
                // 获取当前的过滤条件
                var filter = [];
                if (view.dataset && view.dataset.domain) {
                    filter = filter.concat(view.dataset.domain);
                }
                
                // 如果有搜索视图，获取搜索视图的过滤条件
                if (view.getParent() && view.getParent().searchview) {
                    var searchview = view.getParent().searchview;
                    var search_data = searchview.build_search_data();
                    if (search_data && search_data.domains) {
                        for (var i = 0; i < search_data.domains.length; i++) {
                            filter = filter.concat(search_data.domains[i]);
                        }
                    }
                }
                
                // 获取当前的上下文
                var ctx = {};
                if (view.dataset && view.dataset.context) {
                    ctx = new instance.web.CompoundContext(ctx, view.dataset.context);
                }
                
                // 使用 model.domain() 获取完整的 domain
                var domain = model.domain(filter);
                
                // 使用 model.context() 获取完整的 context
                var context = model.context(ctx);
                
                // 使用 pyeval.eval 对 domain 和 context 进行解析
                var eval_context = instance.web.pyeval.eval('contexts', [context]);
                var eval_domain = instance.web.pyeval.eval('domains', [domain], eval_context);

                // 获取排序信息
                var order_by = view.dataset && view.dataset.sort ? view.dataset.sort : [];
                // var sort = instance.web.serialize_sort(order_by);
                
                console.log("Filter:", filter);
                console.log("Model domain:", domain);
                console.log("Evaluated domain:", eval_domain);
                console.log("Context:", ctx);
                console.log("Model context:", context);
                console.log("Evaluated context:", eval_context);
                console.log("Order by:", order_by);
                // console.log("Sort:", sort);
            } catch (e) {
                console.error("Error getting domain or context:", e);
                var eval_domain = view.dataset ? view.dataset.domain || [] : [];
                var eval_context = view.dataset ? view.dataset.context || {} : {};
                var sort = '';
            }
            
            // 获取当前页面的总记录数
            var total_records = 0;
            if (view.dataset) {
                // 如果 dataset 有 _length 属性，直接使用
                if (view.dataset._length !== undefined) {
                    total_records = view.dataset._length;
                }
                // 如果有 ids，使用 ids 的长度
                else if (view.dataset.ids) {
                    total_records = view.dataset.ids.length;
                }
                
                console.log("Total records:", total_records);
            }
            
            // 发送请求到后端，包含完整的 domain、context、sort 和总记录数
            view.session.get_file({
                url: '/web/export/xls_view_all',
                data: {data: JSON.stringify({
                    model: view.model,
                    ids: view.dataset.ids || [],  // 当前页面的记录IDs
                    fields: export_columns_keys,
                    headers: export_columns_names,
                    domain: eval_domain,  // 使用解析后的 domain
                    context: eval_context, // 使用解析后的 context
                    // sort: sort,            // 排序条件
                    total_records: total_records  // 当前页面的总记录数
                })},
                complete: $.unblockUI
            });
        }
    });

};



// model: 
// fields: this._fields || false,
// domain: instance.web.pyeval.eval('domains',
//         [this._model.domain(this._filter)]),
// context: instance.web.pyeval.eval('contexts',
//         [this._model.context(this._context)]),
// offset: this._offset,
// limit: this._limit,
// sort: instance.web.serialize_sort(this._order_by)
