"""
设置界面模块 - 提供统一的配置界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Dict, Callable
from . import configs_data

class SettingsWindow:
    def __init__(self, parent, callback: Callable = None):
        """
        初始化设置窗口
        parent: 父窗口
        callback: 配置更新后的回调函数
        """
        self.window = tk.Toplevel(parent)
        self.window.title("其他设置")
        self.window.geometry("600x400")
        self.callback = callback
        
        # 加载当前配置
        self.current_config = self.load_current_config()
        
        self.setup_ui()
        
        # 绑定右键双击关闭窗口
        self.window.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
    def setup_ui(self):
        """设置UI界面"""
        # 创建主Canvas用于滚动
        self.canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.canvas)
        
        # 配置Canvas滚动
        self.main_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 布局Canvas和滚动条
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建数据路径配置区域
        self.create_data_path_section()
        
        # 这里可以添加更多配置区域...
        
        # 创建按钮区域
        self.create_button_area()
        
    def create_data_path_section(self):
        """创建数据路径配置区域"""
        # 添加说明标签
        ttk.Label(
            self.main_frame,
            text="数据路径配置",
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
        
        # 创建配置框架
        path_frame = ttk.LabelFrame(self.main_frame, text="路径设置", padding=10)
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 数据目录选择
        data_dir_frame = ttk.Frame(path_frame)
        data_dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(data_dir_frame, text="数据目录:").pack(side=tk.LEFT)
        self.data_dir_entry = ttk.Entry(data_dir_frame)
        self.data_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.data_dir_entry.insert(0, self.current_config.get('data_dir', 'data'))
        
        ttk.Button(
            data_dir_frame,
            text="浏览",
            command=self.browse_directory
        ).pack(side=tk.LEFT)
        
        # 子目录包含选项
        self.include_subdirs_var = tk.BooleanVar(
            value=self.current_config.get('include_subdirs', True)
        )
        ttk.Checkbutton(
            path_frame,
            text="包含子目录",
            variable=self.include_subdirs_var
        ).pack(anchor='w', pady=5)
        
        # 文件扩展名
        ext_frame = ttk.Frame(path_frame)
        ext_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(ext_frame, text="文件扩展名:").pack(side=tk.LEFT)
        self.file_ext_entry = ttk.Entry(ext_frame)
        self.file_ext_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.file_ext_entry.insert(0, self.current_config.get('file_extension', '.json'))
        
    def create_button_area(self):
        """创建按钮区域"""
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # 应用按钮 - 使用高亮颜色
        self.apply_button = tk.Button(
            button_frame,
            text="应用更改",
            command=self.apply_changes,
            bg='light green',
            activebackground='green'
        )
        self.apply_button.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        ttk.Button(
            button_frame,
            text="取消",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
    def browse_directory(self):
        """浏览选择目录"""
        directory = filedialog.askdirectory(
            initialdir=self.data_dir_entry.get()
        )
        if directory:
            self.data_dir_entry.delete(0, tk.END)
            self.data_dir_entry.insert(0, directory)
            # 将焦点重新设置到设置窗口
            self.window.focus_force()
            # 确保窗口显示在最前面
            self.window.lift()
            
    def load_current_config(self) -> Dict:
        """加载当前配置"""
        try:
            if os.path.exists(configs_data.CONFIG_FILE):
                with open(configs_data.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
        return configs_data.DATA_PATHS
        
    def apply_changes(self):
        """应用更改"""
        try:
            # 获取新的配置
            new_config = {
                'data_dir': self.data_dir_entry.get().strip(),
                'include_subdirs': self.include_subdirs_var.get(),
                'file_extension': self.file_ext_entry.get().strip()
            }
            
            # 验证配置
            if not new_config['data_dir']:
                raise ValueError("数据目录不能为空")
            if not new_config['file_extension']:
                raise ValueError("文件扩展名不能为空")
                
            # 尝试创建目录，如果失败则使用默认目录
            try:
                os.makedirs(new_config['data_dir'], exist_ok=True)
            except Exception as e:
                messagebox.showwarning(
                    "警告",
                    f"创建目录失败: {str(e)}\n将使用默认目录",
                    parent=self.window
                )
                new_config['data_dir'] = configs_data.DATA_PATHS['data_dir']
                
            # 保存配置
            os.makedirs(os.path.dirname(configs_data.CONFIG_FILE), exist_ok=True)
            with open(configs_data.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)
                
            # 调用回调函数
            if self.callback:
                self.callback(new_config)
                
            messagebox.showinfo(
                "成功",
                "配置已保存，正在重新加载数据...",
                parent=self.window
            )
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "错误",
                f"保存配置失败: {str(e)}",
                parent=self.window
            )

def get_config() -> Dict:
    """获取当前配置"""
    try:
        if os.path.exists(configs_data.CONFIG_FILE):
            with open(configs_data.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"读取配置文件失败: {str(e)}")
    return configs_data.DATA_PATHS 