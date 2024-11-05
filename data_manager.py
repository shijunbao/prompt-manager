"""
数据管理模块

版本日志：
v1.0 2024-03-xx
- 初始版本
- 实现JSON文件的读写操作
- 实现分组管理功能
- 实现提示词缓存功能
v1.1 2024-03-xx
- 添加data目录管理
- 修改所有文件操作路径到data目录
"""

import json
import os
import re
from typing import List, Dict
import zipfile
import time
from configs.configs_data import DATA_PATHS
from configs.set_configs import get_config

class DataManager:
    def __init__(self):
        # 加载配置的数据目录
        config = get_config()
        self.data_dir = config.get('data_dir', DATA_PATHS['data_dir'])
        
        # 检查配置的目录是否存在，如果不存在则使用默认目录
        if not os.path.exists(self.data_dir):
            print(f"警告: 配置的数据目录 {self.data_dir} 不存在，将使用默认目录")
            self.data_dir = DATA_PATHS['data_dir']  # 使用默认的 data 目录
            
            # 更新配置文件中的目录设置
            try:
                config['data_dir'] = self.data_dir
                config_path = os.path.join('configs', 'user_configs.json')
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"更新配置文件失败: {str(e)}")
        
        self.ensure_data_directory()
        self.data_all = []
        
    def ensure_data_directory(self):
        """确保data目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def get_data_path(self, filename: str) -> str:
        """获取数据文件的完整路径"""
        return os.path.join(self.data_dir, filename)
        
    def load_all_json_data(self) -> List[Dict]:
        """加载所有JSON文件数据"""
        json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        json_data = []
        
        for file in json_files:
            try:
                with open(self.get_data_path(file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    json_data.append(data)
            except:
                print(f"读取json文件数据错误请检查json文件: {file}")
        
        self.data_all = json_data
        return json_data

    def get_all_groups(self) -> List[str]:
        """获取所有分组"""
        groups = set()
        for file in os.listdir(self.data_dir):
            if file.endswith('.json'):
                try:
                    with open(self.get_data_path(file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        group = data.get('group', '').strip()
                        if group:
                            groups.add(group)
                except Exception as e:
                    print(f"读取分组错误: {file}, {str(e)}")
        return sorted(list(groups))  # 排序返回，保证顺序一致

    def save_prompt(self, filename: str, data: Dict):
        """保存提示词数据到文件"""
        with open(self.get_data_path(filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_files_by_group(self, group: str) -> List[str]:
        """获取指定分组的所有文件"""
        files = []
        for file in os.listdir(self.data_dir):
            if file.endswith('.json'):
                try:
                    with open(self.get_data_path(file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('group', '').strip() == group:
                            files.append(file)
                except:
                    print(f"读取文件错误: {file}")
        return files

    def cache_prompt(self, content: str):
        """缓存提示词内容"""
        cache_path = self.get_data_path('cache_prompt.txt')
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def read_cached_prompt(self) -> str:
        """读取缓存的提示词"""
        try:
            cache_path = self.get_data_path('cache_prompt.txt')
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
            
    def delete_prompt(self, filename: str):
        """删除提示词文件"""
        file_path = self.get_data_path(filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    def get_all_files(self) -> List[str]:
        """获取所有JSON文件"""
        return [f for f in os.listdir(self.data_dir) if f.endswith('.json')]

    def export_prompts(self, export_path: str):
        """导出所有提示词到指定路径"""
        export_data = []
        for file in self.get_all_files():
            try:
                with open(self.get_data_path(file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    export_data.append(data)
            except Exception as e:
                print(f"导出文件错误: {file}, {str(e)}")
                
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=4)

    def import_prompts(self, import_path: str):
        """从指定文件导入提示词"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
                
            for data in import_data:
                name = data.get('name', '').strip()
                if name:
                    filename = self.get_safe_filename(name)
                    self.save_prompt(filename, data)
        except Exception as e:
            print(f"导入文件错误: {str(e)}")

    def backup_data(self):
        """备份所有数据"""
        backup_dir = os.path.join(self.data_dir, 'backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.zip')
        
        with zipfile.ZipFile(backup_file, 'w') as zf:
            for file in self.get_all_files():
                zf.write(self.get_data_path(file), file)

    def get_statistics(self) -> Dict:
        """获取提示词统计信息"""
        stats = {
            'total_prompts': 0,
            'total_groups': 0,
            'prompts_by_group': {},
            'most_used_prompts': []
        }
        
        # 统计总数和分组数据
        groups = self.get_all_groups()
        stats['total_groups'] = len(groups)
        
        for group in groups:
            files = self.get_files_by_group(group)
            stats['total_prompts'] += len(files)
            stats['prompts_by_group'][group] = len(files)
            
        return stats

    def get_safe_filename(self, name: str) -> str:
        """生成安全的文件名（移除非法字符）"""
        # 移除或替换不安全的字符
        safe_name = re.sub(r'\W+', '_', name)
        # 确保文件名不重复
        base_name = safe_name
        counter = 1
        while os.path.exists(self.get_data_path(f"{safe_name}.json")):
            safe_name = f"{base_name}_{counter:04d}"
            counter += 1
        return f"{safe_name}.json"

    def get_hotkeys_prompts(self):
        """获取所有带快捷键的提示词"""
        hotkeys_prompts = []
        for file in self.get_all_files():
            try:
                with open(self.get_data_path(file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'shortcut' in data and data['shortcut']:
                        hotkeys_prompts.append(data)
            except Exception as e:
                print(f"读取文件 {file} 出错: {str(e)}")
        return hotkeys_prompts

    def clear_all_hotkeys(self):
        """清空所有 JSON 数据的 shortcut 字段"""
        json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        
        for file in json_files:
            try:
                with open(self.get_data_path(file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'shortcut' in data:
                    data['shortcut'] = ''
                with open(self.get_data_path(file), 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"清空快捷键时出错: {str(e)}")