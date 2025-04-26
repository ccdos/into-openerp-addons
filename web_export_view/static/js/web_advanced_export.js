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

    instance.web.Sidebar.include({
        redraw: function() {
            var self = this;
            this._super.apply(this, arguments);
            self.$el.find('.oe_sidebar').append(QWeb.render('AddExportViewMain', {widget: self}));
            self.$el.find('.oe_sidebar_export_view_xls').on('click', self.on_sidebar_export_view_xls);
            self.$el.find('.oe_sidebar_export_all_xls').on('click', self.on_sidebar_export_all_xls);
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

    });
    
    instance.web.Sidebar.include({
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
            
            // 获取当前过滤条件
            var domain = [];
            var combined_domain = [];
            
            // 尝试从不同的地方获取过滤条件
            try {
                // 1. 首先尝试从当前视图的 dataset 中获取
                if (view.dataset && view.dataset.domain) {
                    domain = view.dataset.domain;
                    combined_domain = domain;
                }
                
                // 2. 尝试从搜索视图中获取
                if (view.getParent() && view.getParent().searchview) {
                    var searchview = view.getParent().searchview;
                    var search_data = searchview.build_search_data();
                    if (search_data && search_data.domains) {
                        // 将搜索视图的域与当前域组合
                        var search_domains = search_data.domains || [];
                        for (var i = 0; i < search_domains.length; i++) {
                            combined_domain = combined_domain.concat(search_domains[i]);
                        }
                    }
                }
                
                // 3. 如果上述方法都没有获取到域，尝试其他方法
                if (!combined_domain || combined_domain.length === 0) {
                    if (view.dataset && view.dataset.context && view.dataset.context.domain) {
                        combined_domain = view.dataset.context.domain;
                    }
                }
                
                // 打印过滤条件以便调试
                console.log("Original domain:", domain);
                console.log("Combined domain:", combined_domain);
            } catch (e) {
                console.error("Error getting domain:", e);
                combined_domain = domain; // 出错时使用原始域
            }
            
            // 发送请求到后端
            $.blockUI();
            view.session.get_file({
                url: '/web/export/xls_view_all',
                data: {data: JSON.stringify({
                    model: view.model,
                    domain: combined_domain,  // 使用组合后的过滤条件
                    fields: export_columns_keys,
                    headers: export_columns_names,
                })},
                complete: $.unblockUI
            });
        }
    });

};
