"""
搜索管理模块

版本日志：
v1.0 2024-03-xx
- 初始版本
- 实现全局搜索功能
- 实现分类内搜索功能
- 实现搜索结果高亮
"""

import re
import json
from typing import List, Dict, Tuple

class SearchManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
    def global_search(self, keyword: str) -> List[Tuple[str, Dict]]:
        """全局搜索
        返回: [(文件名, 文件数据), ...]
        """
        if not keyword:
            return []
            
        results = []
        for file in self.data_manager.get_all_files():
            try:
                with open(self.data_manager.get_data_path(file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 搜索所有字段
                    if self._search_in_data(keyword, data):
                        results.append((file, data))
            except Exception as e:
                print(f"搜索文件出错: {file}, {str(e)}")
        return results
        
    def group_search(self, keyword: str, group: str) -> List[Tuple[str, Dict]]:
        """分组内搜索
        返回: [(文件名, 文件数据), ...]
        """
        if not keyword or not group:
            return []
            
        results = []
        for file in self.data_manager.get_files_by_group(group):
            try:
                with open(self.data_manager.get_data_path(file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if self._search_in_data(keyword, data):
                        results.append((file, data))
            except Exception as e:
                print(f"搜索文件出错: {file}, {str(e)}")
        return results
        
    def _search_in_data(self, keyword: str, data: Dict) -> bool:
        """在数据中搜索关键词"""
        keyword = keyword.lower()
        # 搜索所有文本字段
        for field in ['name', 'content', 'comment', 'group']:
            if keyword in str(data.get(field, '')).lower():
                return True
        return False
        
    def get_highlight_ranges(self, text: str, keyword: str) -> List[Tuple[int, int]]:
        """获取需要高亮的文本范围
        返回: [(开始位置, 结束位置), ...]
        """
        if not keyword or not text:
            return []
            
        ranges = []
        keyword = re.escape(keyword.lower())
        text_lower = text.lower()
        
        for match in re.finditer(keyword, text_lower):
            ranges.append((match.start(), match.end()))
            
        return ranges 