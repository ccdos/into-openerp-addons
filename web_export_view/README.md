# Web Export View 模块

## 功能介绍

Web Export View 是一个 OpenERP 7.0 的实用工具模块，它扩展了 OpenERP 的导出功能，提供了以下特性：

1. **导出当前视图** - 允许用户导出当前正在查看的列表视图数据到 Excel 文件中
2. **导出全部记录** - 允许用户导出当前过滤条件下的所有记录，而不仅仅是当前页面显示的记录

这个模块解决了标准 OpenERP 导出功能的一些限制，让用户能够更便捷地导出数据。

## 使用方法

### 安装

1. 将模块放置在 OpenERP 的 addons 目录中
2. 更新模块列表
3. 安装 "Export Current View" 模块

### 使用

1. 打开任意列表视图（如客户列表、产品列表等）
2. 在右侧边栏中，您将看到一个 "Export Current View" 按钮
3. 点击该按钮，会出现两个选项：
    - **Excel (当前页)** - 导出当前页面显示的记录
    - **Excel (全部记录)** - 导出当前过滤条件下的所有记录
4. 选择所需的导出选项，系统将生成 Excel 文件并自动下载

### 特点

- 导出的 Excel 文件包含列表视图中显示的所有字段
- 支持各种数据类型的正确显示（文本、数字、日期、关联字段等）
- 支持复杂的过滤条件，包括包含 `context_today()` 等函数的表达式
- 关联字段（如 many2one）会显示名称而不是 ID，使导出的数据更具可读性

## 开发过程中的关键要点

### 1. 导出当前视图的实现

原始模块通过扩展 Sidebar 组件，在侧边栏添加导出按钮，收集当前列表视图的数据并发送到后端。关键代码：

```javascript
// 前端：收集当前视图数据
export_columns_keys = [];
export_columns_names = [];
$.each(view.visible_columns, function(){
    if(this.tag=='field'){
        export_columns_keys.push(this.id);
        export_columns_names.push(this.string);
    }
});
rows = view.$el.find('.oe_list_content > tbody > tr');
```

```python
# 后端：处理导出请求
@openerpweb.httprequest
def index(self, req, data, token):
    data = json.loads(data)
    model = data.get('model', [])
    columns_headers = data.get('headers', [])
    rows = data.get('rows', [])
```

### 2. 全部记录导出功能改造

我们对导出功能进行了全面改造，使其能够正确处理复杂的过滤条件和时间表达式。主要改进包括：

#### 2.1 前端获取完整的 domain、context 和排序信息

```javascript
// 获取完整的 domain
var domain = [];
if (view.dataset && view.dataset.domain) {
    domain = domain.concat(view.dataset.domain);
}

// 如果有搜索视图，获取搜索视图的 domain
if (view.getParent() && view.getParent().searchview) {
    var searchview = view.getParent().searchview;
    var search_data = searchview.build_search_data();
    if (search_data && search_data.domains) {
        for (var i = 0; i < search_data.domains.length; i++) {
            domain = domain.concat(search_data.domains[i]);
        }
    }
}

// 使用 model.domain() 和 model.context() 获取完整的 domain 和 context
var model = new instance.web.Model(view.model);
var domain = model.domain(filter);
var context = model.context(ctx);

// 使用 pyeval.eval 对 domain 和 context 进行解析
var eval_domain = instance.web.pyeval.eval('domains', [domain], eval_context);
var eval_context = instance.web.pyeval.eval('contexts', [context]);
```

#### 2.2 后端解析复杂 domain 表达式

我们创建了一个专门的 `parse_domain` 方法，用于解析复杂的 domain 表达式，特别是包含时间表达式的 domain：

```python
def parse_domain(self, domain):
    """
    解析复杂的 domain 表达式，特别是包含时间表达式的 domain
    """
    # 导入需要的模块
    from openerp.tools.safe_eval import safe_eval
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    import time

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
    dom_eval = safe_eval(dom, eval_context)
```

这使得我们能够正确处理如下形式的复杂 domain：

```python
[u"[('formula_date', '>=', (context_today() + relativedelta(years=-1, month=1, day=1)).strftime('%Y-%m-%d')), ('formula_date', '<=', (context_today() + relativedelta(years=-1, month=12, day=31)).strftime('%Y-%m-%d'))]"]  
```

#### 2.3 获取当前页面的总记录数

我们添加了获取当前页面总记录数的功能，并将其传递给后端：

```javascript
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
}

// 将总记录数传递给后端
total_records: total_records
```

#### 2.4 使用 search_read 方法提高效率

我们使用 `search_read` 方法一次性获取所有符合条件的记录，这比先 `search` 再 `read` 更高效：

```python
# 使用 search_read 方法一次性获取所有符合条件的记录
result = Model.search_read(parsed_domain, fields, 0, False, order, user_context)
```

### 3. 改造后的优势

1. **支持复杂的过滤条件**：能够正确处理包含 `context_today()` 等函数的复杂 domain 表达式
2. **完整的上下文信息**：获取并使用完整的 context 信息
3. **正确的排序**：将当前视图的排序信息传递给后端
4. **高效数据获取**：使用 `search_read` 方法一次性获取数据，提高效率
5. **总记录数信息**：获取并传递当前页面的总记录数

这些改进使得导出功能更加完善，能够准确地导出用户在界面上看到的数据，即使是带有复杂过滤条件的数据。
    return req.make_response(
        self.from_data(columns_headers, rows),
        headers=[
            ('Content-Disposition', 'attachment; filename="%s"'
             % self.filename(model)),
            ('Content-Type', self.content_type)
        ],
        cookies={'fileToken': token}
    )
```

### 2. 导出全部记录的实现

为了支持导出当前过滤条件下的所有记录，我们添加了新的功能：

1. **前端修改**：
    - 添加了新的导出选项 "Excel (全部记录)"
    - 收集当前视图的模型名称、字段列表和过滤条件
    - 将这些信息发送到后端

2. **后端修改**：
    - 创建了新的控制器 `ExcelExportViewAll`
    - 使用 ORM 的 `search` 和 `read` 方法获取所有符合条件的记录
    - 处理各种数据类型，使导出的数据更具可读性

### 3. 处理复杂的过滤条件

处理包含 `context_today()` 等函数的过滤条件是一个挑战。我们通过以下方式解决：

```python
def _eval_domain(self, req, domain):
    """使用OpenERP原生方法处理domain表达式
    
    处理包含context_today()等函数的domain表达式
    """
    # 创建评估上下文
    eval_context = {
        'context_today': get_today,
        'datetime': datetime,
        'relativedelta': relativedelta,
        # ...其他必要的上下文变量
    }

    # 使用safe_eval评估domain表达式
    domain = safe_eval(domain[0], eval_context)

    # 使用OpenERP原生的normalize_domain方法处理domain
    return expression.normalize_domain(domain)
```

### 4. 数据类型处理

为了确保导出的数据正确显示，我们对不同类型的数据进行了特殊处理：

```python
# 首先检查是否为False或None，确保这些值被转换为空字符串
if value is False or value is None:
    value = u''
# 处理不同类型的数据，使其更可读
elif isinstance(value, (int, long, float)):
    value = unicode(value)
elif isinstance(value, tuple) and len(value) == 2:
    # 这可能是一个 many2one 字段，格式为 (id, name)
    value = value[1] if value[1] else u''
# ...其他类型的处理
```

## 注意事项

1. 导出大量数据可能需要较长时间，请耐心等待
2. 模块使用了 OpenERP 7.0 的技术栈，如果需要在更高版本中使用，需要进行相应的调整
3. 导出功能依赖于 `xlwt` 库，确保系统中已安装该库

## 贡献者

- 原始模块由 Agile Business Group 开发
- 扩展功能（导出全部记录）由 IntoERP 团队开发

## 许可证

AGPL-3
