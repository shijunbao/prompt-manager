import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import json
import re
import keyboard
import threading
import pyperclip

'''
用法：
https://zhuanlan.zhihu.com/p/675379682?

热键举例：
Python的keyboard库支持的hotkey组合主要包括以下几种：

单个键：例如，'a'，'b'，'c'等。

组合键：例如，'ctrl'，'alt'，'shift'，'space'等。

按键组合：例如，'ctrl+a'，'ctrl+c'，'ctrl+v'，'alt+f4'，'shift+a'等。

按键序列：例如，'a+b'，'a+b+c'等。

按键序列组合：例如，'a+b, c+d'，'a+b, c+d, e+f'等。

按键序列和组合键的组合：例如，'a+b, c+d, e+f, g+h'等。

按键组合： 列如， 'ctrl+alt+c',  'shift+alt+b'等等

注意，keyboard库的add_hotkey函数只接受按键序列和组合键的组合，例如'a+b, c+d'。


'''




'''
 
version（commit）

006 增加修改按钮,加载有问题的json时候的容错（忽略掉错误）
005 增加每个提示词使用热键
004 增加参数设置，界面优化
003 清理无效代码
002 全局热键最新选中的prompt到剪切板，静态磁盘缓存鼠标在列表最新选中的prompt
001 分组，预留八个json字段以备扩充功能
0 列表，新建，删除。
'''


'''
参数设置
'''
#提示词正文文字大小
font_content_size = 18

# 名称文字大小
font_name_size = 17
# 热键文字大小
font_shortcut_size = 10
# 备注文字大小
font_comment_size = 12


# 分组列表文字大小
font_group_size = 15
# 文件列表文字大小
font_list_size = 15

# 分组列表宽度
group_list_width = 15
# 文件列表宽度
file_list_width = 19

#状态栏文本大小
status_size = 15
#状态栏长度
status_width = 30




class App:
    def __init__(self, root):
        self.root = root
        
        self.currentfile = ""
        
        # 创建一个新的容器
        list_frame = tk.Frame(root)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, anchor='w')
        
        # 分组列表
        self.select_group_list = []
        self.group_list = tk.Listbox(list_frame, width=group_list_width, font=('Arial', font_list_size))
        self.group_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.group_list.bind('<<ListboxSelect>>', self.load_files_from_group)
        
        # 文件列表
        self.file_list = tk.Listbox(list_frame, width=file_list_width, font=('Arial', font_list_size))
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_list.bind('<<ListboxSelect>>', self.load_file)
        
        
        # 右侧显示json字段内容
        self.name_label = tk.Label(root, text="Name:")
        self.name_label.pack(side=tk.TOP,anchor='w')         
        self.file_pname = tk.Text(root, height=1, font=('Arial', font_name_size))
        self.file_pname.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        self.group_label = tk.Label(root, text="Group:")
        self.group_label.pack(side=tk.TOP,anchor='w')          
        self.file_pgroup = tk.Text(root,height=1, font=('Arial', font_group_size))
        self.file_pgroup.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        self.name_label = tk.Label(root, text="Shortcut:")
        self.name_label.pack(side=tk.TOP,anchor='w')         
        self.file_pshortcut = tk.Text(root, height=1, font=('Arial', font_shortcut_size))
        self.file_pshortcut.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        self.name_label = tk.Label(root, text="Comment:")
        self.name_label.pack(side=tk.TOP,anchor='w')         
        self.file_pcomment = tk.Text(root, height=3, font=('Arial', font_comment_size))
        self.file_pcomment.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        self.name_label = tk.Label(root, text="Content:")
        self.name_label.pack(side=tk.TOP,anchor='w')         
        self.file_content = tk.Text(root, height= 12, font=('Arial', font_content_size))
        self.file_content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 备用字段：
        self.file_padd1 = tk.Text(root)
        self.file_padd1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  
        self.file_padd1.pack_forget()  #隐藏
        
        self.file_padd2 = tk.Text(root)
        self.file_padd2.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  
        self.file_padd2.pack_forget()  #隐藏   
        
        self.file_padd3 = tk.Text(root)
        self.file_padd3.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  
        self.file_padd3.pack_forget()  #隐藏   
        
        self.file_padd4 = tk.Text(root)
        self.file_padd4.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  
        self.file_padd4.pack_forget()  #隐藏  
        
        self.file_padd5 = tk.Text(root)
        self.file_padd5.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  
        self.file_padd5.pack_forget()  #隐藏        
        
        self.file_padd6 = tk.Text(root)
        self.file_padd6.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  
        self.file_padd6.pack_forget()  #隐藏  
        
        self.file_padd7 = tk.Text(root)
        self.file_padd7.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  
        self.file_padd7.pack_forget()  #隐藏  
        
        self.file_padd8 = tk.Text(root)
        self.file_padd8.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  
        self.file_padd8.pack_forget()  #隐藏
        
        
        ## 各种按钮
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, anchor='w')
        
        # 将按钮添加到新的容器中
        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_file)
        self.delete_button.pack(side=tk.LEFT)  
        
        # 在delete button 右侧增加一个标签，显示固定文字：”当前选中的提示词“
        self.label1 = tk.Label(button_frame, text="当前选中的提示词",font=("Arial", status_size))
        self.label1.pack(side=tk.LEFT)
    
       # 在这个标签的右侧  增加一个标签，背景色为浅绿色，长度为15个字符，文本大小为15
        self.label2 = tk.Label(button_frame, text="", bg="light green", width=status_width, font=("Arial",  status_size))
        self.label2.pack(side=tk.LEFT)   
        
        # 创建一个新的容器,靠右排雷
        button_frame_right = tk.Frame(root)
        button_frame_right.pack(side=tk.RIGHT)
        
        # 将按钮添加到新的容器中
        
        # 添加项目
        self.add_button = tk.Button(button_frame_right, text="新建提示词", command=self.add_file)
        self.add_button.pack(side=tk.LEFT)   
        
        # 保存项目的修改
        self.save_button = tk.Button(button_frame_right, text="保存修改", command=self.save_changes)
        self.save_button.pack(side=tk.LEFT)        
        
        self.copy_button = tk.Button(button_frame_right, text="Copy", command=self.copy_content)
        self.copy_button.pack(side=tk.LEFT)               
        
        self.data_all = []
        
        #初始化  载入组，文件名，数据值。
        #读取每个文件时有容错。
        self.load_groups()
        self.load_files()
        self.data_all = self.load_jsons()
    
    # 载入数据的文件名。
    def load_files(self):
        self.file_list.delete(0, tk.END)
        for file in os.listdir():
            if file.endswith('.json'):
                try:
                    self.file_list.insert(tk.END, file)
                except:
                    print("读取files到列表错误 。。。")

    def load_file(self, event):        
        file = self.file_list.get(self.file_list.curselection())
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                # 预处理  清空字段变量内容  在操作前清理
                self.file_content.delete('1.0', tk.END)
                self.file_pname.delete('1.0', tk.END)
                self.file_pshortcut.delete('1.0', tk.END)
                self.file_pcomment.delete('1.0', tk.END)
                self.file_pgroup.delete('1.0', tk.END)
                #清空备用字段变量
                self.file_padd1.delete('1.0', tk.END)
                self.file_padd2.delete('1.0', tk.END)
                self.file_padd3.delete('1.0', tk.END)
                self.file_padd4.delete('1.0', tk.END)
                self.file_padd5.delete('1.0', tk.END)
                self.file_padd6.delete('1.0', tk.END)
                self.file_padd7.delete('1.0', tk.END)
                self.file_padd8.delete('1.0', tk.END)
                
                # 添加            
                self.file_pname.insert(tk.END, f"{data['name']}\n")
                self.file_pshortcut.insert(tk.END, f"{data['shortcut']}\n")
                self.file_content.insert(tk.END, f"{data['content']}\n")
                self.file_pcomment.insert(tk.END, f"{data['comment']}\n")            
                self.file_pgroup.insert(tk.END, f"{data['group']}\n")
                
                #加载备用字段
                self.file_padd1.insert(tk.END, f"{data['add1']}\n")
                self.file_padd2.insert(tk.END, f"{data['add2']}\n")
                self.file_padd3.insert(tk.END, f"{data['add3']}\n")
                self.file_padd4.insert(tk.END, f"{data['add4']}\n")
                self.file_padd5.insert(tk.END, f"{data['add5']}\n")
                self.file_padd6.insert(tk.END, f"{data['add6']}\n")
                self.file_padd7.insert(tk.END, f"{data['add7']}\n")
                self.file_padd8.insert(tk.END, f"{data['add8']}\n")
        
        except:
            print("读取一个文件出错：    " + file)
            
        self.cache_prompt(self.file_content)
        # 添加
        #for item in self.select_group_list:
            #self.file_list.insert(tk.END, item)
        
        #刷新当前文件名
        self.currentfile = file
        self.label2.config(text=self.currentfile)
        
        
        
        
    # 加载分组        
    def load_groups(self):
        
        # Clear the group list
        self.group_list.delete(0, tk.END)        
        
        # Get all json files in the current directory
        files = [f for f in os.listdir('.') if f.endswith('.json')]
    
        # Load each file and get the 'group' field
        for file in files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    group = data.get('group', None)
                    
                    # If the group is not None and not already in the list, add it
                    if group is not None and group.strip() not in [x.strip() for x in self.group_list.get(0, tk.END)]:
                        
                        self.group_list.insert(tk.END, group)  
            except:
                print("读取json文件的分组group错误：    " + file)
                    
   #从选中的分组中加载json文件名到列表。                
    def load_files_from_group(self, event):        
        # Clear the file list
        self.file_list.delete(0, tk.END)
    
        # Get the selected group 获取选中的group名称        
        group = self.group_list.get(self.group_list.curselection())
              
            
        # Get all json files in the current directory
        files = [f for f in os.listdir('.') if f.endswith('.json')]
    
        # Load each file and get the 'group' field   获取json中的goup字段值
        for file in files:
            with open(file, 'r') as f:
                data = json.load(f)
                file_group = data.get('group', None).strip()
                
                
                # 比较两个group值，处理添加列表逻辑流程。
                # If the file's group is the same as the selected group, add the file to the list
                if file_group == group:
                    self.file_list.insert(tk.END, file) 
        self.select_group_list = list(self.file_list.get(0, tk.END))
                
            
    def base_json(self):
        data = {
            'name': 'My Name',
            'shortcut': 'ctrl+*',
            'content': 'This is my content',
            'comment': '备注信息',
            'group': '000常用',
            'add1': '',
            'add2': '',
            'add3': '',
            'add4': '',
            'add5': '',
            'add6': '',
            'add7': '',
            'add8': ''            
        }
        
        # 将字典写入JSON文件
        with open('base_json.json', 'w') as f:
            json.dump(data, f)  
        self.load_files()
    
    # 获取所有磁盘中的json数据  ，列表每个元素是json转换为字典的所有值。  
    def load_jsons(self):
        json_files = [pos_json for pos_json in os.listdir(os.curdir) if pos_json.endswith('.json')]
        json_data = []
        for file in json_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    json_data.append(data)
            except:
                print("读取json文件数据错误请检查json文件：     " + file)
        return json_data    
            
    def delete_file(self):
        
        selected_files = self.file_list.curselection()
        
        for index in selected_files:
            file = self.file_list.get(index)
            os.remove(file)
        self.load_files() 
        self.load_groups()
        
    def add_file(self):
        name = self.file_pname.get("1.0", "end-1c").strip()        
        name1 = re.sub(r'\W+', '_', name)  # Replace non-alphanumeric characters with underscore
        shortcut = self.file_pshortcut.get("1.0", "end-1c").strip()           
        comment = self.file_pcomment.get("1.0", "end-1c").strip()
        content = self.file_content.get("1.0", "end-1c").strip()
        group = self.file_pgroup.get("1.0", "end-1c").strip()
    
        data = {
                'name': name,
                'group': group,
                'shortcut': shortcut,
                'comment': comment,
                'content': content,                
                'add1': '',
                'add2': '',
                'add3': '',
                'add4': '',
                'add5': '',
                'add6': '',
                'add7': '',
                'add8': ''  
            }
        
        # Check if the file exists
        i = 0
        while os.path.exists(name1 + ".json"):
            i += 1
            name1 = re.sub(r'\W+', '_', name) + "_{:04d}".format(i)        
        
        with open(name1 + ".json", "w") as f:
            json.dump(data, f)  
            
        #self.load_files()
               
        self.load_groups()
    
    # 保存当前界面的各种文本，prompt等，保存到选中的文件中。    
    def save_changes(self):
        name = self.file_pname.get("1.0", "end-1c").strip()        
        shortcut = self.file_pshortcut.get("1.0", "end-1c").strip()           
        comment = self.file_pcomment.get("1.0", "end-1c").strip()
        content = self.file_content.get("1.0", "end-1c").strip()
        group = self.file_pgroup.get("1.0", "end-1c").strip()
    
        data = {
                'name': name,
                'group': group,
                'shortcut': shortcut,
                'comment': comment,
                'content': content,                
                'add1': '',
                'add2': '',
                'add3': '',
                'add4': '',
                'add5': '',
                'add6': '',
                'add7': '',
                'add8': ''  
            }
    
        # 将字典保存为json文件
        with open(self.currentfile, 'w') as f:
            json.dump(data, f)    
    
    # copy 按钮调用    
    def copy_content(self, event=None):
        # 清空剪贴板
        self.root.clipboard_clear()
        # 获取文本内容
        content = self.file_content.get("1.0", tk.END)
        # 将文本内容添加到剪贴板
        self.root.clipboard_append(content)    
        
    # 缓存prompt的内容也就是self.file_content组件的值到磁盘。
    def cache_prompt(self, file_content):        
        file_content = file_content.get("1.0", "end-1c")
        with open('cache_prompt.txt', 'w') as f:
            f.write(file_content)    
        print("缓存promt完成：")
        print(file_content)
    
    # 读取缓存prompt 放入剪切板中， 执行粘贴    
    def send_cache_prompt_toclipboard(self):
        with open('cache_prompt.txt', 'r') as f:
            content = f.read()    
            pyperclip.copy(content)  # 放入剪切板
            clipboard_content = pyperclip.paste()  #粘贴    

#########################################################################################
#类外的函数    

    # 创建一个新的线程来运行keyboard.wait()
    t = threading.Thread(target=keyboard.wait)
    t.start()

root = tk.Tk()
app = App(root)

# 加载每一个热键。
# 加载每一个热键。
hotkeys = []
for item in app.data_all:
    if item['shortcut'] is not None: #非空
        if item['shortcut'] != 'ctrl+*':                
            try:
                hotkey = str(item['shortcut'])
                content = str(item['content'])
                keyboard.add_hotkey(hotkey, lambda content=content: pyperclip.copy(content))
                hotkeys.append((hotkey, content))
            except:
                pass            
            
#全局热键 统一热键
keyboard.add_hotkey("ctrl+b", app.send_cache_prompt_toclipboard)
   
# 创建一个新的线程来运行keyboard.wait()
t_each_hotkey_prompt = threading.Thread(target=keyboard.wait)
t_each_hotkey_prompt.start()

#初始化
# 创建种子json
app.base_json()

root.mainloop()
