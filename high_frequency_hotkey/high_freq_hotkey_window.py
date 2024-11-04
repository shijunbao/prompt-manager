import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import keyboard
import pyperclip
from typing import Dict, Optional

class HotkeyConfigPanel:
    """单个快捷键配置面板"""
    def __init__(self, parent: tk.Frame, index: int):
        self.frame = tk.Frame(parent)
        self.frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.index = index
        self.current_prompt: Optional[Dict] = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        # 快捷键配置区
        hotkey_label = tk.Label(self.frame, text=f"快捷键 {self.index}:", width=10)
        hotkey_label.pack(side=tk.LEFT, padx=5)
        
        self.hotkey_entry = tk.Entry(self.frame, width=15)
        self.hotkey_entry.pack(side=tk.LEFT, padx=5)
        
        # 应用按钮
        self.apply_button = tk.Button(
            self.frame,
            text=f"应用到高频快捷键{self.index}",
            state=tk.DISABLED
        )
        self.apply_button.pack(side=tk.LEFT, padx=5)
        
        # 结果显示
        self.result_label = tk.Label(
            self.frame, 
            text="当前未配置",
            width=30,
            anchor='w'
        )
        self.result_label.pack(side=tk.LEFT, padx=5)
        
    def set_callback(self, callback):
        """设置应用按钮的回调函数"""
        self.apply_button.config(command=lambda: callback(self))
        
    def enable(self):
        """启用应用按钮"""
        self.apply_button.config(state=tk.NORMAL)
        
    def disable(self):
        """禁用应用按钮"""
        self.apply_button.config(state=tk.DISABLED)
        
    def get_config(self) -> Dict:
        """获取当前配置"""
        return {
            'hotkey': self.hotkey_entry.get().strip(),
            'prompt': self.current_prompt
        }
        
    def set_config(self, config: Dict):
        """设置配置"""
        self.hotkey_entry.delete(0, tk.END)
        self.hotkey_entry.insert(0, config.get('hotkey', ''))
        self.current_prompt = config.get('prompt')
        if self.current_prompt:
            self.result_label.config(text=f"已绑定: {self.current_prompt.get('name', '未命名')}")
        else:
            self.result_label.config(text="当前未配置")

class HighFreqHotkeyWindow:
    def __init__(self, parent, data_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("高频快捷键管理")
        self.window.geometry("1000x800")
        self.data_manager = data_manager
        
        # 绑定右键双击事件到窗口
        self.window.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 当前选中的提示词数据
        self.current_prompt = None
        
        # 快捷键配置管理器
        self.hotkey_configs = {}
        
        # 确保配置目录存在
        self.config_dir = os.path.join('high_frequency_hotkey')
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
        self.setup_ui()
        self.load_data()
        self.load_hotkey_configs()

    def setup_ui(self):
        """设置UI界面"""
        # 添加红色加粗提示语句
        tip_frame = ttk.Frame(self.window)
        tip_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        tip_frame.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        tip_label = ttk.Label(tip_frame, 
                             text="鼠标右键双击任意位置关闭本窗口", 
                             font=('Arial', 10, 'bold'),
                             foreground='red')
        tip_label.pack(pady=5)
        tip_label.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 为每个创建的组件添加右键双击事件
        def add_right_click_binding(widget):
            widget.bind('<Double-Button-3>', lambda e: self.window.destroy())
            # 如果是容器类组件,为其子组件也添加绑定
            if isinstance(widget, (tk.Frame, ttk.Frame)):
                for child in widget.winfo_children():
                    add_right_click_binding(child)
        
        self.create_search_frame()
        self.create_list_frame()
        self.create_content_frame()
        self.create_hotkey_frame()
        
        # 为所有已创建的组件添加右键双击事件
        add_right_click_binding(self.window)

    def create_search_frame(self):
        """创建搜索框架"""
        search_frame = tk.Frame(self.window)
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        search_frame.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 全局搜索
        global_search_label = tk.Label(search_frame, text="全局搜索:")
        global_search_label.pack(side=tk.LEFT)
        
        self.global_search_entry = tk.Entry(search_frame)
        self.global_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 20))
        self.global_search_entry.bind('<KeyRelease>', self.on_global_search)
        
        # 分组搜索
        group_search_label = tk.Label(search_frame, text="当前分组搜索:")
        group_search_label.pack(side=tk.LEFT)
        
        self.group_search_entry = tk.Entry(search_frame)
        self.group_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.group_search_entry.bind('<KeyRelease>', self.on_group_search)

    def on_global_search(self, event):
        """处理全局搜索"""
        keyword = self.global_search_entry.get().strip()
        # 清除分组搜索的内容，避免冲突
        self.group_search_entry.delete(0, tk.END)
        
        if not keyword:
            self.refresh_lists()  # 清空搜索时恢复原始显示
            return
            
        # 清空当前列表
        self.group_list.delete(0, tk.END)
        self.file_list.delete(0, tk.END)
        
        # 执行搜索
        for file in self.data_manager.get_all_files():
            try:
                with open(self.data_manager.get_data_path(file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 搜索所有字段
                    if self._search_in_data(keyword, data):
                        group = data.get('group', '')
                        if group not in [self.group_list.get(i) for i in range(self.group_list.size())]:
                            self.group_list.insert(tk.END, group)
                        self.file_list.insert(tk.END, file)
            except Exception as e:
                print(f"搜索文件出错: {file}, {str(e)}")

    def on_group_search(self, event):
        """处理分组搜索"""
        if not self.group_list.curselection():
            return
            
        keyword = self.group_search_entry.get().strip()
        # 清除全局搜索的内容，避免冲突
        self.global_search_entry.delete(0, tk.END)
        
        group = self.group_list.get(self.group_list.curselection())
        
        if not keyword:
            self.load_files_from_group(None)  # 清空搜索时恢复原始显示
            return
            
        # 清空文件列表
        self.file_list.delete(0, tk.END)
        
        # 执行搜索
        for file in self.data_manager.get_files_by_group(group):
            try:
                with open(self.data_manager.get_data_path(file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if self._search_in_data(keyword, data):
                        self.file_list.insert(tk.END, file)
            except Exception as e:
                print(f"搜索文件出错: {file}, {str(e)}")

    def _search_in_data(self, keyword: str, data: Dict) -> bool:
        """在数据中搜索关键词"""
        keyword = keyword.lower()
        # 搜索所有文本字段
        for field in ['name', 'content', 'comment', 'group']:
            if keyword in str(data.get(field, '')).lower():
                return True
        return False

    def refresh_lists(self):
        """刷新列表"""
        # 刷新分组列表
        self.group_list.delete(0, tk.END)
        groups = self.data_manager.get_all_groups()
        for group in groups:
            self.group_list.insert(tk.END, group)

    def create_hotkey_frame(self):
        """创建快捷键配置区域"""
        # 创建一个Frame来容纳滚动条和内容
        outer_frame = tk.Frame(self.window)
        outer_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(outer_frame)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        
        # 创建内部Frame来放置所有配置面板
        self.hotkey_frame = tk.Frame(canvas)
        
        # 配置Canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 打包滚动条和Canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 在Canvas中创建窗口来显示内部Frame
        canvas.create_window((0, 0), window=self.hotkey_frame, anchor="nw")
        
        # 创建15个配置面板
        self.config_panels = []
        for i in range(15):
            panel = HotkeyConfigPanel(self.hotkey_frame, i + 1)
            panel.set_callback(self.apply_hotkey)
            self.config_panels.append(panel)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 更新Canvas的滚动区域
        def _configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.hotkey_frame.bind('<Configure>', _configure_canvas)

    def load_file(self, event):
        """加载选中的文件内容"""
        if not self.file_list.curselection():
            return
            
        selected_file = self.file_list.get(self.file_list.curselection())
        file_path = self.data_manager.get_data_path(selected_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.current_prompt = data
                
                self.prompt_name_text.delete(1.0, tk.END)
                self.prompt_name_text.insert(tk.END, selected_file)
                self.prompt_content_text.delete(1.0, tk.END)
                self.prompt_content_text.insert(tk.END, data.get('content', ''))
                
                # 启用所有配置面板
                for panel in self.config_panels:
                    panel.enable()
                    panel.current_prompt = data
                    
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {str(e)}")

    def apply_hotkey(self, panel: HotkeyConfigPanel):
        """应用快捷键配置"""
        if not panel.current_prompt:
            return
            
        hotkey = panel.hotkey_entry.get().strip()
        if not hotkey:
            messagebox.showwarning("警告", "请输入快捷键", parent=self.window)
            return
            
        try:
            # 如果该位置已有快捷键，先解除绑定
            if panel.index in self.hotkey_configs:
                old_config = self.hotkey_configs[panel.index]
                keyboard.remove_hotkey(old_config['hotkey'])
                
            # 获取文件名
            filename = self.prompt_name_text.get("1.0", "end-1c").strip()
            
            # 注册新快捷键
            def copy_content():
                # 实时读取prompt内容
                try:
                    file_path = self.data_manager.get_data_path(filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        content = data.get('content', '')
                        pyperclip.copy(content)
                except Exception as e:
                    print(f"读取prompt内容失败: {str(e)}")
                    
            keyboard.add_hotkey(hotkey, copy_content)
            
            # 只保存快捷键和文件名的映射
            self.hotkey_configs[panel.index] = {
                'hotkey': hotkey,
                'filename': filename
            }
            
            # 更新显示
            panel.result_label.config(
                text=f"已绑定: {filename}"
            )
            
            # 保存配置到文件
            self.save_hotkey_configs()
            
            messagebox.showinfo("成功", f"快捷键 {hotkey} 配置成功", parent=self.window)
            
        except Exception as e:
            messagebox.showerror("错误", f"配置快捷键失败: {str(e)}", parent=self.window)

    def load_hotkey_configs(self):
        """加载快捷键配置"""
        try:
            config_path = os.path.join(self.config_dir, 'hotkey_configs.json')
            if not os.path.exists(config_path):
                return
                
            with open(config_path, 'r', encoding='utf-8') as f:
                self.hotkey_configs = json.load(f)
                
            # 恢复配置显示和注册快捷键
            for index_str, config in self.hotkey_configs.items():
                index = int(index_str)
                if 0 <= index - 1 < len(self.config_panels):
                    panel = self.config_panels[index - 1]
                    
                    # 设置显示
                    hotkey = config['hotkey']
                    filename = config['filename']
                    panel.hotkey_entry.delete(0, tk.END)
                    panel.hotkey_entry.insert(0, hotkey)
                    panel.result_label.config(text=f"已绑定: {filename}")
                    
                    # 注册快捷键 - 修改这部分
                    def create_copy_function(filename):
                        def copy_content():
                            # 实时读取prompt内容
                            try:
                                file_path = self.data_manager.get_data_path(filename)
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    content = data.get('content', '')
                                    pyperclip.copy(content)
                            except Exception as e:
                                print(f"读取prompt内容失败: {str(e)}")
                        return copy_content
                    
                    # 使用工厂函数创建独立的回调函数
                    keyboard.add_hotkey(hotkey, create_copy_function(filename))
                    
        except Exception as e:
            messagebox.showerror("错误", f"加载快捷键配置失败: {str(e)}", parent=self.window)

    def save_hotkey_configs(self):
        """保存快捷键配置"""
        try:
            config_path = os.path.join(self.config_dir, 'hotkey_configs.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.hotkey_configs, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("错误", f"保存快捷键配置失败: {str(e)}")

    def create_list_frame(self):
        """创建左侧列表框架"""
        list_frame = tk.Frame(self.window)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, anchor='w')
        list_frame.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 分组列表
        self.group_list = tk.Listbox(list_frame, width=20, font=('Arial', 12))
        self.group_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.group_list.bind('<<ListboxSelect>>', self.load_files_from_group)

        # 文件列表
        self.file_list = tk.Listbox(list_frame, width=30, font=('Arial', 12))
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_list.bind('<<ListboxSelect>>', self.load_file)

    def create_content_frame(self):
        """创建右侧内容框架"""
        content_frame = tk.Frame(self.window)
        content_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        content_frame.bind('<Double-Button-3>', lambda e: self.window.destroy())
        
        # 提示词名称文本框
        self.prompt_name_label = tk.Label(content_frame, text="提示词名称:", font=('Arial', 14))
        self.prompt_name_label.pack(pady=5)  # 减小间距
        self.prompt_name_text = tk.Text(content_frame, height=1, width=50, font=('Arial', 14))
        self.prompt_name_text.pack(pady=5)

        # 提示词内容文本框
        self.prompt_content_label = tk.Label(content_frame, text="提示词内容:", font=('Arial', 14))
        self.prompt_content_label.pack(pady=5)
        self.prompt_content_text = tk.Text(content_frame, height=8, width=50, font=('Arial', 14))  # 减小高度
        self.prompt_content_text.pack(pady=5)

    def load_data(self):
        """初始化数据"""
        # 加载分组列表
        groups = self.data_manager.get_all_groups()
        for group in groups:
            self.group_list.insert(tk.END, group)
            
        # 如果有分组，默认选中第一个分组并加载其文件
        if groups:
            self.group_list.select_set(0)
            self.load_files_from_group(None)  # None 表示不是由事件触发
            
            # 如果有文件，默认选中第一个文件并加载
            if self.file_list.size() > 0:
                self.file_list.select_set(0)
                self.load_file(None)  # None 表示不是由事件触发

    def load_files_from_group(self, event):
        """从选中的分组加载文件"""
        if not self.group_list.curselection():
            return
            
        self.file_list.delete(0, tk.END)
        group = self.group_list.get(self.group_list.curselection())
        files = self.data_manager.get_files_by_group(group)
        
        for file in files:
            self.file_list.insert(tk.END, file)

    # ... (保留原有的其他方法)