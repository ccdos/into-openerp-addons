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
