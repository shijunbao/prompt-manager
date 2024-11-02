"""
删除窗口模块

版本日志：
v1.0 2024-03-xx
- 初始版本
- 实现删除窗口界面
- 实现分组显示功能
- 实现多选删除功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from winotify import Notification, audio

class DeleteWindow:
    def __init__(self, parent, data_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("删除提示词")
        self.window.geometry("800x500")  # 加大窗口尺寸
        self.data_manager = data_manager
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """设置UI界面"""
        # 顶部提示信息框架
        tip_frame = ttk.Frame(self.window)
        tip_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 添加操作提示文本
        tip_text = "操作说明：\n1. 选择左侧分组\n2. 在右侧列表中选择要删除的提示词(按住Ctrl键可多选)\n3. 右键点击选中项，选择\"删除选中项\"进行删除"
        tip_label = ttk.Label(tip_frame, text=tip_text, 
                            font=('Arial', 10),
                            foreground='blue',
                            justify=tk.LEFT,
                            background='light yellow')
        tip_label.pack(fill=tk.X, pady=5)
        
        # 创建左右分栏
        self.paned = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧分组列表框架
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame)
        
        # 分组列表标签
        group_label = ttk.Label(left_frame, text="分组列表")
        group_label.pack(pady=5)
        
        # 分组列表
        self.group_list = tk.Listbox(left_frame, width=20)
        self.group_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.group_list.bind('<<ListboxSelect>>', self.on_group_select)
        
        # 右侧提示词列表框架
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame)
        
        # 提示词列表标签
        prompt_label = ttk.Label(right_frame, text="提示词列表 (可多选)")
        prompt_label.pack(pady=5)
        
        # 提示词列表(支持多选)
        self.prompt_list = tk.Listbox(right_frame, selectmode=tk.EXTENDED)
        self.prompt_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", 
                                command=self.prompt_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.prompt_list.config(yscrollcommand=scrollbar.set)
        
        # 绑定右键菜单
        self.create_context_menu()
        
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="删除选中项", 
                                    command=self.delete_selected,
                                    background='light yellow',
                                    foreground='red')
        self.prompt_list.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        """显示右键菜单"""
        if self.prompt_list.curselection():  # 只在有选中项时显示
            self.context_menu.post(event.x_root, event.y_root)
            
    def load_data(self):
        """加载数据"""
        # 加载分组列表
        groups = self.data_manager.get_all_groups()
        for group in groups:
            self.group_list.insert(tk.END, group)
            
    def on_group_select(self, event):
        """当选择分组时"""
        if not self.group_list.curselection():
            return
            
        # 清空提示词列表
        self.prompt_list.delete(0, tk.END)
        
        # 获取选中的分组
        group = self.group_list.get(self.group_list.curselection())
        
        # 加载该分组的所有文件
        files = self.data_manager.get_files_by_group(group)
        for file in files:
            self.prompt_list.insert(tk.END, file)
            
    def delete_selected(self):
        """删除选中的提示词"""
        selected = self.prompt_list.curselection()
        if not selected:
            return
            
        count = len(selected)
        if not messagebox.askyesno("确认删除", 
                                 f"确定要删除选中的 {count} 个提示词吗？\n此操作不可恢复！"):
            return
            
        success_files = []
        failed_files = []
        
        for index in selected[::-1]:
            file = self.prompt_list.get(index)
            try:
                self.data_manager.delete_prompt(file)
                self.prompt_list.delete(index)
                success_files.append(file)
            except Exception as e:
                failed_files.append(file)
                messagebox.showerror("错误", f"删除文件 {file} 失败: {str(e)}")
        
        # 构建通知消息
        msg = f"删除操作完成\n成功：{len(success_files)}个\n"
        if success_files:
            msg += "\n成功删除的文件：\n" + "\n".join(success_files)
        if failed_files:
            msg += "\n\n删除失败的文件：\n" + "\n".join(failed_files)
        
        self.show_notification(msg)
        
    def show_notification(self, message):
        """显示通知"""
        notification = Notification(
            app_id="提示词小助手",
            title="提示词小助手",
            msg=message,
            duration="long"  # 15秒
        )
        notification.set_audio(audio.Default, loop=False)
        notification.show()