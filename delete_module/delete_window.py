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
#from winotify import Notification, audio

class DeleteWindow:
    def __init__(self, parent, data_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("删除提示词")
        self.data_manager = data_manager
        
        # 绑定右键双击事件到窗口
        self.window.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 添加红色加粗提示语句
        tip_label1 = ttk.Label(main_frame, 
                             text="鼠标右键双击任意位置关闭本窗口", 
                             font=('Arial', 10, 'bold'),
                             foreground='red')
        tip_label1.pack(pady=5)
        tip_label1.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 添加操作提示语句 - 修复引号问题
        tip_label2 = ttk.Label(main_frame, 
                             text='选中提示词（可多选）单击右键，点"删除"可完成删除操作', 
                             font=('Arial', 10, 'bold'),
                             foreground='blue')  # 使用蓝色区分不同类型的提示
        tip_label2.pack(pady=5)
        tip_label2.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 提示标签
        tip_label3 = ttk.Label(main_frame, text="选择要删除的提示词（可多选）")
        tip_label3.pack(pady=5)
        tip_label3.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 列表框架
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        list_frame.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 分组列表 - 单选模式
        self.group_list = tk.Listbox(list_frame, width=30, selectmode=tk.SINGLE)
        self.group_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.group_list.bind('<<ListboxSelect>>', self.on_group_select)
        self.group_list.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 分组列表滚动条
        group_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.group_list.yview)
        group_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.group_list.config(yscrollcommand=group_scrollbar.set)
        group_scrollbar.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 文件列表 - 支持Ctrl和Shift多选
        self.file_list = tk.Listbox(list_frame, width=50, selectmode=tk.EXTENDED)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.file_list.bind('<Double-Button-3>', lambda e: self.window.destroy())
        # 添加右键菜单绑定
        self.file_list.bind('<Button-3>', self.show_context_menu)
        
        # 文件列表滚动条
        file_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_list.yview)
        file_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.file_list.config(yscrollcommand=file_scrollbar.set)
        file_scrollbar.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        button_frame.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 删除按钮
        delete_button = ttk.Button(button_frame, text="删除选中项", command=self.delete_selected)
        delete_button.pack(side=tk.LEFT, padx=5)
        delete_button.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
        cancel_button.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 创建右键菜单
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="删除", command=self.delete_selected)
        
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
        # 只有在选中了prompt条目时才显示右键菜单
        if self.file_list.curselection():
            self.context_menu.post(event.x_root, event.y_root)
            
    def load_data(self):
        """加载数据"""
        # 加载分组
        groups = self.data_manager.get_all_groups()
        for group in groups:
            self.group_list.insert(tk.END, group)
            
        # 默认选中第一个分组并加载其文件
        if groups:
            self.group_list.select_set(0)
            self.on_group_select(None)  # None 表示不是由事件触发
        
    def on_group_select(self, event):
        """处理分组选择事件"""
        if not self.group_list.curselection():
            return
            
        # 清空文件列表
        self.file_list.delete(0, tk.END)
        
        # 获取选中的分组
        group = self.group_list.get(self.group_list.curselection())
        
        # 加载该分组的文件
        files = self.data_manager.get_files_by_group(group)
        for file in files:
            self.file_list.insert(tk.END, file)
            
        # 如果有文件，默认选中第一个
        if self.file_list.size() > 0:
            self.file_list.select_set(0)
        
    def delete_selected(self):
        """删除选中的文件"""
        # 检查是否有选中的prompt条目
        selected = self.file_list.curselection()
        if not selected:
            messagebox.showwarning("警告", "请选择要删除的提示词", parent=self.window)
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的提示词吗？", parent=self.window):
            files_to_delete = [self.file_list.get(i) for i in selected]
            for file in files_to_delete:
                self.data_manager.delete_prompt(file)
                
            # 刷新当前分组的文件列表
            if self.group_list.curselection():
                group = self.group_list.get(self.group_list.curselection())
                self.file_list.delete(0, tk.END)  # 清空文件列表
                
                # 重新加载当前分组的文件
                files = self.data_manager.get_files_by_group(group)
                for file in files:
                    self.file_list.insert(tk.END, file)
            
            # 删除成功提示对话框已移除
            
            # 使用简单的messagebox提示，不使用气泡通知
            messagebox.showinfo("完成", f"已删除 {len(files_to_delete)} 个文件", parent=self.window)
        
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