import tkinter as tk
from tkinter import ttk, messagebox
import json

class EditPromptWindow:
    def __init__(self, parent, data_manager, current_file, content, callback=None):
        self.window = tk.Toplevel(parent)
        self.window.title("编辑提示词内容")
        
        # 获取屏幕尺寸
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 设置窗口大小为全屏
        self.window.geometry(f"{screen_width}x{screen_height}")
        
        self.data_manager = data_manager
        self.current_file = current_file
        self.original_content = content
        self.callback = callback  # 添加回调函数
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        # 按钮框架
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # 保存按钮
        self.save_button = ttk.Button(button_frame, text="保存prompt", command=self.save_content)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        self.exit_button = ttk.Button(button_frame, text="退出", command=self.on_closing)
        self.exit_button.pack(side=tk.LEFT, padx=5)
        
        # 提示标签框架
        tip_frame = ttk.Frame(button_frame)
        tip_frame.pack(side=tk.LEFT, padx=20)
        
        # 右键双击提示
        tip_label1 = ttk.Label(tip_frame, 
                              text="右键双击编辑区域可关闭编辑界面", 
                              font=('Arial', 10), 
                              foreground='gray')
        tip_label1.pack(side=tk.TOP, anchor='w')
        
        # 左键双击提示 - 使用绿色粗体
        tip_label2 = ttk.Label(tip_frame, 
                              text="左键双击编辑区域进行保存", 
                              font=('Arial', 10, 'bold'),  # 添加粗体
                              foreground='green')          # 设置绿色
        tip_label2.pack(side=tk.TOP, anchor='w')
        
        # 创建文本编辑区
        self.content_text = tk.Text(self.window, wrap=tk.WORD, font=('Arial', 14))
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 设置初始内容
        if self.original_content:
            self.content_text.insert('1.0', self.original_content)
            
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.content_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.content_text.yview)
        
        # 绑定关闭窗口事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 绑定右键双击事件关闭窗口
        self.content_text.bind('<Double-Button-3>', lambda e: self.on_closing())
        
        # 绑定左键双击事件保存内容
        self.content_text.bind('<Double-Button-1>', lambda e: self.save_content_with_flash())
        
        # 绑定保存按钮按下和释放事件
        self.save_button.bind('<ButtonPress-1>', self.on_save_press)
        self.save_button.bind('<ButtonRelease-1>', self.on_save_release)
        
        # 设置焦点到文本框
        self.content_text.focus_set()
        
    def save_content(self):
        """保存内容到JSON文件"""
        try:
            # 读取当前JSON文件
            with open(self.data_manager.get_data_path(self.current_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新content字段
            content = self.content_text.get('1.0', 'end-1c')
            data['content'] = content
            
            # 保存回文件
            with open(self.data_manager.get_data_path(self.current_file), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            # 更新原始内容（用于检查是否有改动）
            self.original_content = content
            
            # 更新缓存
            self.data_manager.cache_prompt(content)
            
            # 调用回调函数更新主界面
            if self.callback:
                self.callback(self.original_content)
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}", parent=self.window)
        
    def save_content_with_flash(self):
        """保存内容并闪烁提示"""
        try:
            # 读取当前JSON文件
            with open(self.data_manager.get_data_path(self.current_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新content字段
            content = self.content_text.get('1.0', 'end-1c')
            data['content'] = content
            
            # 保存回文件
            with open(self.data_manager.get_data_path(self.current_file), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            # 更新原始内容（用于检查是否有改动）
            self.original_content = content
            
            # 更新缓存
            self.data_manager.cache_prompt(content)
            
            # 调用回调函数更新主界面
            if self.callback:
                self.callback(self.original_content)
            
            # 闪烁效果
            self.content_text.configure(bg='light green')
            self.window.after(200, lambda: self.content_text.configure(bg='white'))
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}", parent=self.window)
        
    def on_save_press(self, event):
        """保存按钮按下效果"""
        self.content_text.configure(bg='light green')
        
    def on_save_release(self, event):
        """保存按钮释放效果"""
        self.content_text.configure(bg='white')
        self.save_content()
        
    def has_changes(self):
        """检查内容是否有改动"""
        current_content = self.content_text.get('1.0', 'end-1c')
        return current_content != self.original_content
        
    def on_closing(self):
        """关闭窗口前检查是否需要保存"""
        if self.has_changes():
            response = messagebox.askyesnocancel(
                "保存更改",
                "内容已修改，是否保存？",
                parent=self.window
            )
            
            if response is None:  # 取消关闭
                return
            elif response:  # 是，保存更改
                self.save_content()
                
        self.window.destroy() 