"""
热键管理模块

版本日志：
v1.0 2024-03-xx
- 初始版本
- 实现热键注册功能
- 实现全局热键功能
- 实现热键监听线程
v1.1 2024-03-xx
- 添加热键注册错误处理
- 优化热键验证逻辑
"""

import keyboard
import pyperclip
import threading
from typing import List, Dict

class HotkeyManager:
    def __init__(self):
        self.hotkeys = []
        
    def register_hotkeys(self, data_all: List[dict]):
        """注册所有热键"""
        for item in data_all:
            try:
                # 检查shortcut字段是否存在且有效
                shortcut = item.get('shortcut', '')
                if not shortcut or shortcut == 'ctrl+*':
                    continue
                    
                content = item.get('content', '')
                if not content:
                    continue
                    
                # 注册热键
                keyboard.add_hotkey(shortcut, lambda c=content: pyperclip.copy(c))
                self.hotkeys.append((shortcut, content))
                print(f"成功注册热键: {shortcut}")
                
            except Exception as e:
                print(f"注册热键失败: {str(e)}")
                continue

    def register_global_hotkey(self, hotkey: str, callback):
        """注册全局热键"""
        try:
            keyboard.add_hotkey(hotkey, callback)
            print(f"成功注册全局热键: {hotkey}")
        except Exception as e:
            print(f"注册全局热键失败: {str(e)}")

    def start_listener(self):
        """启动热键监听线程"""
        try:
            thread = threading.Thread(target=keyboard.wait)
            thread.daemon = True
            thread.start()
            print("热键监听线程已启动")
        except Exception as e:
            print(f"启动热键监听线程失败: {str(e)}") 