"""
GUI界面模块

版本日志：
v1.0 2024-03-xx
- 初始版本
- 实现基础GUI界面
- 实现提示词编辑功能
- 实现分组显示功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config import FONT_SIZES, LAYOUT, BASE_JSON_TEMPLATE
from search_manager import SearchManager
import pyperclip
import re
import os
import json

class PromptAssistantGUI:
    def __init__(self, root: tk.Tk, data_manager, hotkey_manager):
        self.root = root
        self.data_manager = data_manager
        self.hotkey_manager = hotkey_manager
        self.search_manager = SearchManager(data_manager)  # 添加搜索管理器
        self.current_file = ""
        self.select_group_list = []
        
        self.setup_ui()
        self.init_data()
        
    def init_data(self):
        """初始化数据"""
        # 加载分组列表
        groups = self.data_manager.get_all_groups()
        for group in groups:
            self.group_list.insert(tk.END, group)
            
        # 如果有分组，默认选中第一个分组载其文件
        if groups:
            self.group_list.select_set(0)
            self.load_files_from_group(None)  # None 表示不是由事件触发
            
            # 如果有文件，默认选中第一个文件并加载
            if self.file_list.size() > 0:
                self.file_list.select_set(0)
                self.load_file(None)  # None 表示不是由事件触发
        
    def setup_ui(self):
        """设置UI界面"""
        # 创建顶部按钮和状态栏区域
        top_frame = ttk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # 左侧按钮组
        left_button_frame = ttk.Frame(top_frame)
        left_button_frame.pack(side=tk.LEFT)
        
        self.delete_button = ttk.Button(left_button_frame, text="Delete", command=self.show_delete_window)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # 状态显示标签
        self.label1 = ttk.Label(left_button_frame, text="当前选中的提示词", 
                             font=("Arial", FONT_SIZES['status']))
        self.label1.pack(side=tk.LEFT, padx=5)
        
        self.label2 = ttk.Label(left_button_frame, text="", background="light green", 
                             width=LAYOUT['status_width'], 
                             font=("Arial", FONT_SIZES['status']))
        self.label2.pack(side=tk.LEFT, padx=5)
        
        # 右侧按钮组
        right_button_frame = ttk.Frame(top_frame)
        right_button_frame.pack(side=tk.RIGHT)
        
        # 功能按钮
        self.hotkeys_button = ttk.Button(right_button_frame, text="独立专属快捷键", command=self.open_hotkeys_window)
        self.hotkeys_button.pack(side=tk.LEFT, padx=5)
        
        self.high_freq_hotkey_button = ttk.Button(right_button_frame, text="高频快捷键管理", command=self.open_high_freq_hotkey_window)
        self.high_freq_hotkey_button.pack(side=tk.LEFT, padx=5)
        
        self.add_button = tk.Button(right_button_frame, text="新建提示词")
        self.add_button.pack(side=tk.LEFT, padx=5)
        self.add_button.bind('<ButtonPress-1>', self.on_add_button_press)
        self.add_button.bind('<ButtonRelease-1>', self.on_add_button_release)
        
        self.save_button = tk.Button(right_button_frame, text="保存修改")
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.save_button.bind('<ButtonPress-1>', self.on_save_button_press)
        self.save_button.bind('<ButtonRelease-1>', self.on_save_button_release)
        
        self.copy_button = ttk.Button(right_button_frame, text="Copy", command=self.copy_content)
        self.copy_button.pack(side=tk.LEFT, padx=5)
        
        self.exit_button = ttk.Button(right_button_frame, text="退出", command=self.root.destroy)
        self.exit_button.pack(side=tk.LEFT, padx=(20, 10))
        
        # 创建其他界面元素
        self.create_search_frame()
        self.create_list_frame()
        self.create_content_frame()
        
    def create_search_frame(self):
        """创建搜索框架"""
        search_frame = tk.Frame(self.root)
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # 全局搜索
        global_search_label = tk.Label(search_frame, text="全局搜索:")
        global_search_label.pack(side=tk.LEFT)
        
        self.global_search_entry = tk.Entry(search_frame)
        self.global_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 20))
        self.global_search_entry.bind('<KeyRelease>', self.on_global_search)
        
        # 分组搜索 - 修改标签文本
        group_search_label = tk.Label(search_frame, text="当前分组搜索:")
        group_search_label.pack(side=tk.LEFT)
        
        self.group_search_entry = tk.Entry(search_frame)
        self.group_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.group_search_entry.bind('<KeyRelease>', self.on_group_search)
        
    def create_list_frame(self):
        """创建左侧列表框架"""
        list_frame = tk.Frame(self.root)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, anchor='w')
        
        # 分组列表
        self.group_list = tk.Listbox(list_frame, width=LAYOUT['group_list_width'], 
                                   font=('Arial', FONT_SIZES['list']))
        self.group_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.group_list.bind('<<ListboxSelect>>', self.load_files_from_group)
        
        # 文件列表
        self.file_list = tk.Listbox(list_frame, width=LAYOUT['file_list_width'], 
                                  font=('Arial', FONT_SIZES['list']))
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_list.bind('<<ListboxSelect>>', self.load_file)
        
    def create_content_frame(self):
        """创建右侧内容框架"""
        # 主框架
        content_frame = tk.Frame(self.root)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建可滚动的内容区域
        # 使用PanedWindow来确保内容区域和按钮区域的分隔
        paned = ttk.PanedWindow(content_frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建内容区域的容器
        detail_container = ttk.Frame(paned)
        paned.add(detail_container, weight=1)
        
        # 创建可滚动的文本区域
        self.detail_text = tk.Text(detail_container, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(detail_container, orient="vertical", command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=scrollbar.set)
        
        # 打包动条和文区域
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建内部Frame作为内容容器
        self.detail_frame = ttk.Frame(self.detail_text)
        self.detail_text.window_create("1.0", window=self.detail_frame)
        
        # 绑定鼠标滚轮事件到所有文本框和标签
        def _on_mousewheel(event):
            self.detail_text.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # 为每个组件绑定滚轮事件
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            # 递归绑定所有子组件
            for child in widget.winfo_children():
                bind_mousewheel(child)
                # 特殊处理Text组件
                if isinstance(child, tk.Text):
                    child.bind("<MouseWheel>", lambda e: "break")  # 阻止Text组件的默认滚动行为
        
        # 绑定主容器及其所有子组件
        bind_mousewheel(self.detail_frame)
        
        # 为detail_text本也绑定滚轮事件
        self.detail_text.bind("<MouseWheel>", _on_mousewheel)
        
        # 提示词名称
        name_frame = ttk.Frame(self.detail_frame)
        name_frame.pack(fill=tk.X, padx=10, pady=5)
        self.name_label = ttk.Label(name_frame, text="Name:", font=('Arial', FONT_SIZES['name']))
        self.name_label.pack(side=tk.TOP, anchor='w')
        self.file_pname = tk.Text(name_frame, height=1, font=('Arial', FONT_SIZES['name']))
        self.file_pname.pack(fill=tk.X, pady=2)
        
        # 分组
        group_frame = ttk.Frame(self.detail_frame)
        group_frame.pack(fill=tk.X, padx=10, pady=5)
        self.group_label = ttk.Label(group_frame, text="Group:", font=('Arial', FONT_SIZES['group']))
        self.group_label.pack(side=tk.TOP, anchor='w')
        self.file_pgroup = tk.Text(group_frame, height=1, font=('Arial', FONT_SIZES['group']))
        self.file_pgroup.pack(fill=tk.X, pady=2)
        
        # 独立专属快捷键
        shortcut_frame = ttk.Frame(self.detail_frame)
        shortcut_frame.pack(fill=tk.X, padx=10, pady=5)
        self.shortcut_label = ttk.Label(shortcut_frame, text="独立专属快捷键:", font=('Arial', FONT_SIZES['shortcut']))
        self.shortcut_label.pack(side=tk.TOP, anchor='w')
        self.file_pshortcut = tk.Text(shortcut_frame, height=1, font=('Arial', FONT_SIZES['shortcut']))
        self.file_pshortcut.pack(fill=tk.X, pady=2)
        
        # 备注
        comment_frame = ttk.Frame(self.detail_frame)
        comment_frame.pack(fill=tk.X, padx=10, pady=5)
        self.comment_label = ttk.Label(comment_frame, text="Comment:", font=('Arial', FONT_SIZES['comment']))
        self.comment_label.pack(side=tk.TOP, anchor='w')
        self.file_pcomment = tk.Text(comment_frame, height=3, font=('Arial', FONT_SIZES['comment']))
        self.file_pcomment.pack(fill=tk.X, pady=2)
        
        # 修改content标签文本
        self.content_label = ttk.Label(content_frame, 
                                     text="双击content编辑区域进行放大编辑", 
                                     font=('Arial', FONT_SIZES['content']))
        self.content_label.pack(side=tk.TOP, anchor='w')
        
        # 内容
        content_frame = ttk.Frame(self.detail_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.file_content = tk.Text(content_frame, height=24, font=('Arial', FONT_SIZES['content']))
        self.file_content.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # 禁用主Text组件的编辑功能
        self.detail_text.configure(state='disabled')
        
        # 在所有组件创建完成后，再次绑定滚轮事件（确保新创建的组件都被绑定）
        bind_mousewheel(self.detail_frame)
        
        # 在创建file_content后添加双击事件绑定
        self.file_content.bind('<Double-Button-1>', self.open_edit_window)
        
    def load_files_from_group(self, event):
        """从选中的分组加载文件"""
        if not self.group_list.curselection():
            return
            
        self.file_list.delete(0, tk.END)
        group = self.group_list.get(self.group_list.curselection())
        files = self.data_manager.get_files_by_group(group)
        
        for file in files:
            self.file_list.insert(tk.END, file)
        self.select_group_list = files
        
    def load_file(self, event):
        """加载选中的文件"""
        if (event is None and self.file_list.size() > 0) or (event and self.file_list.curselection()):
            if event is None:
                index = 0
            else:
                index = self.file_list.curselection()[0]
            
            file = self.file_list.get(index)
            self.current_file = file
            self.label2.config(text=file)
            
            self.clear_text_fields()
            
            try:
                with open(self.data_manager.get_data_path(file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"加载文件内容: {data}")
                    self.fill_text_fields(data)
                    self.data_manager.cache_prompt(data['content'])
                    
                    # 如果当前有搜索关键词，立即高亮显示
                    global_keyword = self.global_search_entry.get().strip()
                    group_keyword = self.group_search_entry.get().strip()
                    if global_keyword:
                        self.highlight_text(global_keyword)
                    elif group_keyword:
                        self.highlight_text(group_keyword)
                    
            except Exception as e:
                print(f"加载文件错误: {file}, {str(e)}")
                messagebox.showerror("错误", f"加载文件失败: {str(e)}")
            
    def clear_text_fields(self):
        """清空所有文本框"""
        self.file_pname.delete('1.0', tk.END)
        self.file_pgroup.delete('1.0', tk.END)
        self.file_pshortcut.delete('1.0', tk.END)
        self.file_pcomment.delete('1.0', tk.END)
        self.file_content.delete('1.0', tk.END)
        
    def fill_text_fields(self, data):
        """填充文本框"""
        try:
            self.clear_text_fields()
            
            self.file_pname.insert(tk.END, data.get('name', ''))
            self.file_pgroup.insert(tk.END, data.get('group', ''))
            self.file_pshortcut.insert(tk.END, data.get('shortcut', ''))
            self.file_pcomment.insert(tk.END, data.get('comment', ''))
            self.file_content.insert(tk.END, data.get('content', ''))
            
            print("文本框填充完成")
        except Exception as e:
            print(f"填充文本框错误: {str(e)}")
        
    def add_file(self):
        """添加文件"""
        name = self.file_pname.get("1.0", "end-1c").strip()
        if not name:
            return
            
        name1 = re.sub(r'\W+', '_', name)
        
        data = {
            'name': name,
            'group': self.file_pgroup.get("1.0", "end-1c").strip(),
            'shortcut': self.file_pshortcut.get("1.0", "end-1c").strip(),
            'comment': self.file_pcomment.get("1.0", "end-1c").strip(),
            'content': self.file_content.get("1.0", "end-1c").strip(),
            'add1': '', 'add2': '', 'add3': '', 'add4': '',
            'add5': '', 'add6': '', 'add7': '', 'add8': ''
        }
        
        filename = f"{name1}.json"
        i = 0
        while os.path.exists(self.data_manager.get_data_path(filename)):
            i += 1
            filename = f"{name1}_{i:04d}.json"
        
        try:
            self.data_manager.save_prompt(filename, data)
            # 保存到缓存
            self.data_manager.cache_prompt(data['content'])
            self.refresh_lists()
        except Exception as e:
            messagebox.showerror("错误", f"创建提示词失败：{str(e)}")
        
    def save_changes(self):
        """保存修改"""
        if not self.current_file:
            return
            
        data = {
            'name': self.file_pname.get("1.0", "end-1c").strip(),
            'group': self.file_pgroup.get("1.0", "end-1c").strip(),
            'shortcut': self.file_pshortcut.get("1.0", "end-1c").strip(),
            'comment': self.file_pcomment.get("1.0", "end-1c").strip(),
            'content': self.file_content.get("1.0", "end-1c").strip(),
            'add1': '', 'add2': '', 'add3': '', 'add4': '',
            'add5': '', 'add6': '', 'add7': '', 'add8': ''
        }
        
        try:
            self.data_manager.save_prompt(self.current_file, data)
            # 保存到缓存
            self.data_manager.cache_prompt(data['content'])
        except Exception as e:
            messagebox.showerror("错误", f"保存修改失败：{str(e)}")
        
    def delete_file(self):
        """删除文件"""
        if not self.file_list.curselection():
            return
            
        file = self.file_list.get(self.file_list.curselection())
        self.data_manager.delete_prompt(file)
        self.refresh_lists()
        
    def copy_content(self):
        """复制内容到剪贴板"""
        content = self.file_content.get("1.0", tk.END)
        pyperclip.copy(content)
        
    def refresh_lists(self):
        """新列表"""
        # 刷新分组列表
        self.group_list.delete(0, tk.END)
        groups = self.data_manager.get_all_groups()
        for group in groups:
            self.group_list.insert(tk.END, group)
            
    def send_cache_prompt_toclipboard(self):
        """发送缓存的提示词到剪贴板"""
        content = self.data_manager.read_cached_prompt()
        if content:
            pyperclip.copy(content)
        
    def on_global_search(self, event):
        """处理全局搜索"""
        keyword = self.global_search_entry.get().strip()
        # 清除分组搜索的内容，避免冲突
        self.group_search_entry.delete(0, tk.END)
        
        if not keyword:
            self.refresh_lists()  # 清空搜索时恢复始显示
            return
            
        # 清空当前列表
        self.group_list.delete(0, tk.END)
        self.file_list.delete(0, tk.END)
        
        # 执行搜索
        results = self.search_manager.global_search(keyword)
        
        # 显示结果
        shown_groups = set()
        for file, data in results:
            group = data.get('group', '')
            if group not in shown_groups:
                self.group_list.insert(tk.END, group)
                shown_groups.add(group)
            self.file_list.insert(tk.END, file)
        
        # 高亮显示当前文本框中的匹配内容
        self.highlight_text(keyword)
        
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
        results = self.search_manager.group_search(keyword, group)
        
        # 显示结果
        for file, _ in results:
            self.file_list.insert(tk.END, file)
        
        # 高亮显示当前文本框中的匹配内容
        self.highlight_text(keyword)
        
    def highlight_text(self, keyword):
        """高亮显示匹配的文本"""
        if not keyword:
            return
            
        # 获取所有需要高亮的文本范围
        for widget in [self.file_pname, self.file_content, self.file_pcomment]:
            text = widget.get("1.0", tk.END)
            widget.tag_remove("highlight", "1.0", tk.END)  # 清除现有高亮
            
            ranges = self.search_manager.get_highlight_ranges(text, keyword)
            for start, end in ranges:
                # 将字符位置转换为tkinter的行列格式
                start_line = text.count('\n', 0, start) + 1
                start_col = start - text.rfind('\n', 0, start) - 1
                end_line = text.count('\n', 0, end) + 1
                end_col = end - text.rfind('\n', 0, end) - 1
                
                # 添加高亮标签
                widget.tag_add("highlight", 
                             f"{start_line}.{start_col}", 
                             f"{end_line}.{end_col}")
                widget.tag_config("highlight", background="light green")
        
        # 添加右键菜单
        def create_context_menu(self):
            self.context_menu = tk.Menu(self.root, tearoff=0)
            self.context_menu.add_command(label="删除", command=self.delete_file)
            self.context_menu.add_command(label="复制", command=self.copy_content)
            
            # 绑定右键菜单到文件列表
            self.file_list.bind("<Button-3>", self.show_context_menu)

        def show_context_menu(self, event):
            if self.file_list.curselection():  # 只在有选中项时显示
                self.context_menu.post(event.x_root, event.y_root)

    def show_delete_window(self):
        """显示删除窗口"""
        try:
            from delete_module.delete_window import DeleteWindow
            DeleteWindow(self.root, self.data_manager)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开删除窗口: {str(e)}\n请检查delete_module目录是否存在")
            print(f"打开删除窗口错误: {str(e)}")

    def open_hotkeys_window(self):
        """打开独立专属快捷键配置界面"""
        from hotkeys.hotkeys_window import HotkeysWindow
        HotkeysWindow(self.root, self.data_manager)

    def open_high_freq_hotkey_window(self):
        """打开高频快捷键管理界面"""
        from high_frequency_hotkey.high_freq_hotkey_window import HighFreqHotkeyWindow
        HighFreqHotkeyWindow(self.root, self.data_manager)

    def on_add_button_press(self, event):
        """新建按钮按下时的效果"""
        self.add_button.configure(bg='yellow')  # 按钮变黄
        self.file_list.configure(bg='yellow')   # 列表变黄

    def on_add_button_release(self, event):
        """新建按钮释放时的效果"""
        self.add_button.configure(bg='SystemButtonFace')  # 恢复按钮默认颜色
        self.file_list.configure(bg='white')    # 恢复列表默认颜色
        self.add_file()  # 执行新建操作

    def on_save_button_press(self, event):
        """保存按钮按下时的效果"""
        self.file_content.configure(bg='light green')
        # 记录按下的时间
        self.save_button_press_time = event.time

    def on_save_button_release(self, event):
        """保存按钮释放时的效果"""
        # 计算按下的持续时间（毫秒）
        press_duration = (event.time - self.save_button_press_time) * 1000  # 转换为毫秒
        
        if press_duration < 1000:  # 如果按下时间不足1秒
            # 设置定时器，确保从按下开始算起满1秒后再恢复颜色
            self.root.after(1000, lambda: self.file_content.configure(bg='white'))
        else:
            # 果已经超过1秒，立即恢复颜色
            self.file_content.configure(bg='white')
        
        # 执行保存操作
        self.save_changes()

    def open_edit_window(self, event):
        """打开编辑窗口"""
        if self.current_file:
            from edit_prompt_content import EditPromptWindow
            content = self.file_content.get('1.0', 'end-1c')
            
            # 添加回调函数用于更新主界面内容
            def update_main_content(new_content):
                self.file_content.delete('1.0', tk.END)
                self.file_content.insert('1.0', new_content)
            
            edit_window = EditPromptWindow(
                self.root,
                self.data_manager,
                self.current_file,
                content,
                callback=update_main_content  # 传入回调函数
            )