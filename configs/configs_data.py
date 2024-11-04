"""
配置数据模块 - 存储所有配置参数及默认值
"""

import os

# 数据路径配置
DATA_PATHS = {
    'data_dir': 'data',              # 主数据目录
    'include_subdirs': True,         # 是否包含子目录
    'file_extension': '.json',       # 文件扩展名
}

# 配置文件路径
CONFIG_FILE = os.path.join('configs', 'user_configs.json') 