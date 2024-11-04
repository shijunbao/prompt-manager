"""
主程序入口
"""

import tkinter as tk
from tkinter import messagebox  # 添加messagebox导入
from gui import PromptAssistantGUI
from data_manager import DataManager
from hotkey_manager import HotkeyManager
from config import GLOBAL_HOTKEY
import os
import sys
import traceback
import logging
from datetime import datetime
import json
import pyperclip
import keyboard

# 配置日志
def setup_logging():
    """设置日志"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_file = os.path.join('logs', f'error_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def perform_startup_checks():
    """执行启动自检"""
    try:
        # 检查data目录
        if not os.path.exists('data'):
            os.makedirs('data')
    except Exception as e:
        logging.error(f"启动自检失败: {str(e)}")
        messagebox.showerror("错误", f"启动自检失败: {str(e)}")

def maximize_window(root):
    """跨平台窗口最大化"""
    try:
        # Windows平台
        root.state('zoomed')
    except:
        try:
            # Linux/Unix平台
            root.attributes('-zoomed', True)
        except:
            # 如果以上方法都失败，使用屏幕尺寸
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.geometry(f"{screen_width}x{screen_height}+0+0")

def main():
    try:
        # 设置日志
        setup_logging()
        
        # 执行启动自检
        perform_startup_checks()
        
        root = tk.Tk()
        root.title("提示词小助手")
        
        # 使用跨平台的窗口最大化方法
        maximize_window(root)
        
        # 设置最小窗口大小
        root.minsize(800, 600)
        
        # 初始化数据管理器 - 会自动加载配置的数据目录
        data_manager = DataManager()
        hotkey_manager = HotkeyManager()
        
        # 创建GUI
        app = PromptAssistantGUI(root, data_manager, hotkey_manager)
        
        # 加载数据
        data_all = data_manager.load_all_json_data()
        
        # 注册热键
        hotkey_manager.register_hotkeys(data_all)
        hotkey_manager.register_global_hotkey(
            GLOBAL_HOTKEY, 
            lambda: app.send_cache_prompt_toclipboard()
        )
        hotkey_manager.start_listener()
        
        # 加载高频快捷键配置
        config_dir = os.path.join('high_frequency_hotkey')
        config_path = os.path.join(config_dir, 'hotkey_configs.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    hotkey_configs = json.load(f)
                    
                # 注册所有高频快捷键
                for config in hotkey_configs.values():
                    hotkey = config['hotkey']
                    filename = config['filename']
                    
                    def create_copy_function(filename):
                        def copy_content():
                            try:
                                file_path = data_manager.get_data_path(filename)
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    content = data.get('content', '')
                                    pyperclip.copy(content)
                            except Exception as e:
                                print(f"读取prompt内容失败: {str(e)}")
                        return copy_content
                    
                    keyboard.add_hotkey(hotkey, create_copy_function(filename))
                    
            except Exception as e:
                logging.error(f"加载高频快捷键配置失败: {str(e)}")
        
        root.mainloop()
        
    except Exception as e:
        # 记录错误到日志
        logging.error(f"程序运行错误: {str(e)}")
        logging.error(traceback.format_exc())
        
        # 显示错误消息框
        messagebox.showerror("错误", 
                           f"程序运行出错:\n{str(e)}\n\n详细错误信息已保存到logs目录")
        sys.exit(1)

if __name__ == "__main__":
    main() 