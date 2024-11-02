"""
主程序入口

版本日志：
v1.0 2024-03-xx
- 初始版本
- 实现模块化架构
- 整合各个功能模块
- 优化代码结构
v1.1 2024-03-xx
- 添加窗口最大化显示
- 优化窗口初始化
- 添加启动自检流程
- 添加错误捕获和日志记录
"""

import tkinter as tk
from gui import PromptAssistantGUI
from data_manager import DataManager
from hotkey_manager import HotkeyManager
from config import GLOBAL_HOTKEY
from winotify import Notification, audio
import os
import sys
import traceback
import logging
from datetime import datetime

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

def show_startup_notification():
    """显示启动完成通知"""
    try:
        notification = Notification(
            app_id="提示词小助手",
            title="提示词小助手",
            msg="软件启动完成，已准备就绪！",
            duration="short"
        )
        notification.set_audio(audio.Default, loop=False)
        notification.show()
    except Exception as e:
        logging.error(f"显示启动通知失败: {str(e)}")

def perform_startup_checks():
    """执行启动自检"""
    try:
        # 检查data目录
        if not os.path.exists('data'):
            os.makedirs('data')
            notification = Notification(
                app_id="提示词小助手",
                title="提示词小助手",
                msg="已自动创建data目录",
                duration="short"
            )
            notification.show()
    except Exception as e:
        logging.error(f"启动自检失败: {str(e)}")
        messagebox.showerror("错误", f"启动自检失败: {str(e)}")

def main():
    try:
        # 设置日志
        setup_logging()
        
        # 执行启动自检
        perform_startup_checks()
        
        root = tk.Tk()
        root.title("提示词小助手")
        
        # 设置窗口最大化
        root.state('zoomed')
        
        # 设置最小窗口大小
        root.minsize(800, 600)
        
        # 初始化各个管理器
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
        
        # 显示启动完成通知
        show_startup_notification()
        
        root.mainloop()
        
    except Exception as e:
        # 记录错误到日志
        logging.error(f"程序运行错误: {str(e)}")
        logging.error(traceback.format_exc())
        
        # 显示错误消息框
        from tkinter import messagebox
        messagebox.showerror("错误", 
                           f"程序运行出错:\n{str(e)}\n\n详细错误信息已保存到logs目录")
        
        # 保持窗口显示
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main() 
