"""
配置文件，存储所有配置参数

版本日志：
v1.0 2024-03-xx
- 初始版本
- 添加GUI字体配置
- 添加GUI布局配置
- 添加文件配置
- 添加JSON模板配置
- 添加全局热键配置
"""

# GUI 字体配置
# 定义界面中不同部分的字体大小
FONT_SIZES = {
    'content': 18,    # 提示词正文的字体大小
    'name': 17,       # 提示词名称的字体大小
    'shortcut': 10,   # 快捷键显示的字体大小
    'comment': 12,    # 备注信息的字体大小
    'group': 15,      # 分组名称的字体大小
    'list': 15,       # 左侧列表的字体大小
    'status': 15      # 底部状态栏的字体大小
}

# GUI 布局配置
# 定义界面各个部分的宽度
LAYOUT = {
    'group_list_width': 15,    # 左侧分组列表的宽度（字符数）
    'file_list_width': 19,     # 左侧文件列表的宽度（字符数）
    'status_width': 30         # 底部状态栏的宽度（字符数）
}

# 文件配置
DATA_DIR = 'data'                  # 数据目录名
CACHE_FILE = 'cache_prompt.txt'    # 缓存文件名（将保存在data目录下）
JSON_EXTENSION = '.json'           # 提示词文件的扩展名

# 基础JSON模板
# 新建提示词时的默认值模板
BASE_JSON_TEMPLATE = {
    'name': 'My Name',            # 提示词名称（默认值）
    'shortcut': 'ctrl+*',         # 快捷键（默认值，*表示未设置）
    'content': 'This is my content', # 提示词内容（默认值）
    'comment': '备注信息',          # 备注说明（默认值）
    'group': '000常用',            # 所属分组（默认值）
    'add1': '',                   # 预留扩展字段1
    'add2': '',                   # 预留扩展字段2
    'add3': '',                   # 预留扩展字段3
    'add4': '',                   # 预留扩展字段4
    'add5': '',                   # 预留扩展字段5
    'add6': '',                   # 预留扩展字段6
    'add7': '',                   # 预留扩展字段7
    'add8': ''                    # 预留扩展字段8
}

# 全局热键配置
GLOBAL_HOTKEY = 'ctrl+b'          # 全局快捷键，用于将当前选中的提示词复制到剪贴板

# 添加提示词模板配置
PROMPT_TEMPLATES = {
    '通用模板': {
        'name': '通用提示词',
        'content': '请你扮演{角色}，帮我{任务}。要求：{要求}',
        'comment': '适用于一般场景的通用模板',
        'group': '模板'
    },
    '代码模板': {
        'name': '代码生成',
        'content': '请用{语言}实现{功能}，要求：{要求}',
        'comment': '用于生成代码的模板',
        'group': '模板'
    }
}