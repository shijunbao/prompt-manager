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
from tkinter import filedialog, messagebox
from config import FONT_SIZES, LAYOUT, BASE_JSON_TEMPLATE
from search_manager import SearchManager
import pyperclip
import re
import os
import json
from winotify import Notification, audio

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
            
        # 如果有分组，默认选中第一个分组并加载其文件
        if groups:
            self.group_list.select_set(0)
            self.load_files_from_group(None)  # None 表示不是由事件触发
            
            # 如果有文件，默认选中第一个文件并加载
            if self.file_list.size() > 0:
                self.file_list.select_set(0)
                self.load_file(None)  # None 表示不是由事件触发
        
    def setup_ui(self):
        """设置UI界面"""
        self.create_search_frame()  # 添加搜索框架
        self.create_list_frame()
        self.create_content_frame()
        self.create_button_frame()
        
        # 新增按钮
        self.hotkeys_button = tk.Button(self.root, text="独立专属快捷键", command=self.open_hotkeys_window)
        self.hotkeys_button.pack(side=tk.BOTTOM, pady=10)
        
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
        # 创建名称标签和帮助按钮的容器框架
        name_frame = tk.Frame(self.root)
        name_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        # 左侧容器用于放置Name标签
        left_container = tk.Frame(name_frame)
        left_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 名称标签
        self.name_label = tk.Label(left_container, text="Name:")
        self.name_label.pack(side=tk.LEFT, anchor='w')
        
        # 帮助按钮 - 放在左侧容器中，紧跟Name标签
        help_text = """使用说明：
1. 基本操作:
- 右侧填写prompt名称和内容
- 点击"新建提示词"按钮创建新的prompt
- 点击左侧分组，选择具体prompt
- 或在搜索框中搜索并选择prompt

2. 快捷键说明：
- 默认快捷键：ctrl+b复制当前选中的prompt
- 专属快捷键：如需设置prompt专属的全局快捷键，请在shortcut处填写
注意：专属快捷键不要设置为ctrl+b等高频切换的默认快捷键

更多详细说明请参考readme.md"""

        help_label = tk.Label(left_container, text="使用说明", fg="blue", cursor="hand2")
        help_label.pack(side=tk.LEFT, padx=(10, 0))  # 只设置左边距
        
        # 创建工具提示
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)  # 移除窗口边框
            
            # 获取help_label的位置
            x = help_label.winfo_rootx()
            y = help_label.winfo_rooty() + help_label.winfo_height()
            
            # 设置tooltip位置，确保显示在help_label正下方
            tooltip.wm_geometry(f"+{x}+{y+5}")
            
            # 创建文本标签
            text = tk.Label(tooltip, text=help_text, justify=tk.LEFT,
                           relief=tk.SOLID, borderwidth=1,
                           bg="lightyellow", padx=5, pady=5)
            text.pack()
            
            # 鼠标离开时关闭提示
            def hide_tooltip(event):
                tooltip.destroy()
                
            help_label.bind('<Leave>', hide_tooltip)
            tooltip.bind('<Leave>', hide_tooltip)
            
        help_label.bind('<Enter>', show_tooltip)
        
        # 名称文本框
        self.file_pname = tk.Text(self.root, height=1, font=('Arial', FONT_SIZES['name']))
        self.file_pname.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        # 分组
        self.group_label = tk.Label(self.root, text="Group:")
        self.group_label.pack(side=tk.TOP, anchor='w')
        self.file_pgroup = tk.Text(self.root, height=1, font=('Arial', FONT_SIZES['group']))
        self.file_pgroup.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        # 快捷键
        self.shortcut_label = tk.Label(self.root, text="Shortcut:")
        self.shortcut_label.pack(side=tk.TOP, anchor='w')
        self.file_pshortcut = tk.Text(self.root, height=1, font=('Arial', FONT_SIZES['shortcut']))
        self.file_pshortcut.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        # 备注
        self.comment_label = tk.Label(self.root, text="Comment:")
        self.comment_label.pack(side=tk.TOP, anchor='w')
        self.file_pcomment = tk.Text(self.root, height=3, font=('Arial', FONT_SIZES['comment']))
        self.file_pcomment.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        # 内容
        self.content_label = tk.Label(self.root, text="Content:")
        self.content_label.pack(side=tk.TOP, anchor='w')
        self.file_content = tk.Text(self.root, height=12, font=('Arial', FONT_SIZES['content']))
        self.file_content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
    def create_button_frame(self):
        """创建底部按钮框架"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, anchor='w')
        
        # 修改删除按钮的命令
        self.delete_button = tk.Button(button_frame, text="Delete", command=self.show_delete_window)
        self.delete_button.pack(side=tk.LEFT)
        
        # 状态标签
        self.label1 = tk.Label(button_frame, text="当前选中的提示词", 
                             font=("Arial", FONT_SIZES['status']))
        self.label1.pack(side=tk.LEFT)
        
        self.label2 = tk.Label(button_frame, text="", bg="light green", 
                             width=LAYOUT['status_width'], 
                             font=("Arial", FONT_SIZES['status']))
        self.label2.pack(side=tk.LEFT)
        
        # 右侧按钮框架
        button_frame_right = tk.Frame(self.root)
        button_frame_right.pack(side=tk.RIGHT)
        
        # 新建按钮
        self.add_button = tk.Button(button_frame_right, text="新建提示词", command=self.add_file)
        self.add_button.pack(side=tk.LEFT)
        
        # 保存按钮
        self.save_button = tk.Button(button_frame_right, text="保存修改", command=self.save_changes)
        self.save_button.pack(side=tk.LEFT)
        
        # 复制按
        self.copy_button = tk.Button(button_frame_right, text="Copy", command=self.copy_content)
        self.copy_button.pack(side=tk.LEFT)
        
        # 修改退出按钮 - 加大尺寸
        self.exit_button = tk.Button(button_frame_right, 
                                    text="退出", 
                                    command=self.root.destroy,
                                    fg='green',
                                    width=10,  # 加宽
                                    height=2,  # 加高
                                    font=('Arial', FONT_SIZES['status'] + 2))  # 加大字体
        self.exit_button.pack(side=tk.LEFT, padx=(20, 10), pady=5)  # 增加边距
        
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
            notification = Notification(
                app_id="提示词小助手",
                title="提示词小助手",
                msg="请输入提示词名称",
                duration="short"
            )
            notification.set_audio(audio.Default, loop=False)
            notification.show()
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
            # 显示通知
            notification = Notification(
                app_id="提示词小助手",
                title="提示词小助手",
                msg=f"成功创建新提示词：{name}",
                duration="short"
            )
            notification.set_audio(audio.Default, loop=False)
            notification.show()
        except Exception as e:
            notification = Notification(
                app_id="提示词小助手",
                title="提示词小助手",
                msg=f"创建提示词失败：{str(e)}",
                duration="short"
            )
            notification.set_audio(audio.Default, loop=False)
            notification.show()
        
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
            # 保存到缓存，这样ctrl+b才能获取到最新内容
            self.data_manager.cache_prompt(data['content'])
            # 显示通知
            notification = Notification(
                app_id="提示词小助手",
                title="提示词小助手",
                msg=f"成功保存修改：{data['name']}",
                duration="short"
            )
            notification.set_audio(audio.Default, loop=False)
            notification.show()
        except Exception as e:
            notification = Notification(
                app_id="提示词小助手",
                title="提示词小助手",
                msg=f"保存修改失败：{str(e)}",
                duration="short"
            )
            notification.set_audio(audio.Default, loop=False)
            notification.show()
        
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
        """刷新列表"""
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
            self.refresh_lists()  # 清空搜索时恢复原始显示
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
        from delete_module.delete_window import DeleteWindow
        DeleteWindow(self.root, self.data_manager)

    def show_notification(self, message, duration="short"):
        """显示通知"""
        notification = Notification(
            app_id="提示词小助手",
            title="提示词小助手",
            msg=message,
            duration=duration
        )
        notification.set_audio(audio.Default, loop=False)
        notification.show()

    def open_hotkeys_window(self):
        """打开独立专属快捷键配置界面"""
        from hotkeys.hotkeys_window import HotkeysWindow
        HotkeysWindow(self.root, self.data_manager)