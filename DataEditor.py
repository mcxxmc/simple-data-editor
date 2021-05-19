import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from typing import List, Optional

# from tkinter import ttk
import json

from Stack import Stack


# some static helper function
def listToString(list):
    # 将一个list转换成“a b c”的形式， 方便使用StringVar()
    return " ".join(list)

def stringToList(string):
    # 上面那个函数的反函数
    return string.split(" ")


# 用于Stack的op:
# ops = ["edit_content", "new_entry", "delete_entry"]
# "edit_content"和"delete_entry"的content应该不为空

class DataEditor:

    def __init__(self):

        # 首先定义所有的可编辑的attribute（不包括主窗口以外的静止的界面设计），并指明对应的数据类型。这样方便其他动态方法调用。

        # 用来执行“撤销”和“重做”两个操作的Stack；用来记录已经执行过的操作
        # 这个stack用于“撤销”；任何用户进行的非“撤销”操作都会进入这里
        self.undoStack = Stack()
        # 这个stack用于“重做”；只有“撤销”操作产生的记录才会进入这里
        self.redoStack = Stack()
        # “保存”会清空上面两个stack，而非“撤销”操作会清空redoStack

        # flag
        # if the login page is to be closed
        self.islogin = False

        # if changes are saved
        self.flag_saved = True

        # if the content in the Text (or for each entry) is changed
        self.entry_content_changed = False
        
        # if a new entry is selected by mouse
        self.curse_selection_changed = False

        # 文件路径
        self.path = ""

        # 由json转来的总dict，包含所有词条（也只包含所有词条）
        self.load = {}

        # 目录
        # 目录，数据类型是列表
        self.index = []

        # 被（用户）选中的词条和它对应的内容，数据类型都是string
        self.selectedEntry = ""
        self.selectedContent = ""


        print("First step of initialization has been finished. Starting login process.")

        # 初始的登录窗口，循环直到login完成，得到self.path
        self.login()

        while self.islogin is False:
            print("waiting for login")


        # 最主要的窗口
        self.window = tk.Tk()
        self.window.title("DataBase V4.0")
        self.window.resizable(0, 0)  # 禁止扩大和缩小窗口
        self.window.geometry('1200x720')

        # 一些补充的定义
        # StringVar需要放在Tk()后，否则会返回NoneType error
        self.indexStrObj = tk.StringVar()

        # 上方字幕的文本，类型是StringVar
        self.captionText = tk.StringVar()

        # 读取path对应的Json文件，获取一个字典self.load
        self.loadJson()

        # 更新self.index和self.indexStrObj
        self.updateIndex()


        # 现在，来搭建主界面的所有框架

        # 上方字幕
        self.frameCaption = tk.Frame(self.window, width=1000, height=20)
        # pack在最前面，防止被挤掉（scroll设置了fill参数，会自动填充“空余”空间）
        self.frameCaption.pack(side="top")

        # 下方按钮
        self.frameButtom = tk.Frame(self.window, width=1000, height=200)
        self.frameButtom.pack(side="bottom")

        # index列表
        self.frameIndex = tk.Frame(self.window, width=250, height=500)
        self.frameIndex.pack(side="left")

        # Text文本
        self.frameText = tk.Frame(self.window, width=700, height=500)
        self.frameText.pack(side="right")


        # 首先处理最上面的字幕；它负责显示目前选择的词条和已执行的操作
        self.captionText.set("初始化完成，目前尚无选中的词条")
        self.caption = tk.Label( self.frameCaption, justify='center', textvariable=self.captionText, font=('Arial', 12) )
        self.caption.pack(side='top')

        # 接着处理下方的按钮
        self.editContent = tk.Button(self.frameButtom, text="编辑词条内容", command=self.edit_content, width=50)
        self.editContent.pack(side='top')

        # 然后是左边的index列表
        # 当左边index中内容被双击选中时，在右边显示相应的文本
        self.showIndex = tk.Listbox(self.frameIndex, height=500, width=20, justify='left', listvariable=self.indexStrObj)
        self.showIndex.config(font=('Arial', 14))
        self.scrollbar1 = tk.Scrollbar(self.frameIndex, command=self.showIndex.yview)
        self.scrollbar1.pack(side="right", fill=tk.Y)
        self.showIndex.config(yscrollcommand=self.scrollbar1.set)
        self.showIndex.bind("<Double-Button-1>", self.new_selection)  # By default, Bind函数永远会传递一个self值，所以应该用动态方法
        self.showIndex.pack(side="left")

        # 最后是右边的文本
        self.showText = tk.Text(self.frameText)
        self.showText.config(font=('Arial', 16), width=750, height=26)
        self.showText.insert('end', self.selectedContent)
        self.showText.config(state=tk.DISABLED)             # 内容不可在当前页面更改
        self.scrollbar2 = tk.Scrollbar(self.frameText, command=self.showText.yview)
        self.scrollbar2.pack(side="right", fill=tk.Y)
        self.showText.config(yscrollcommand=self.scrollbar2.set)
        self.showText.pack(side='top')


        # 菜单栏
        self.menubar = tk.Menu(self.window)

        self.filemenu0 = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='文件', menu=self.filemenu0)
        self.filemenu0.add_command(label='保存所有', command=self.save)
        self.filemenu0.add_command(label='搜索词条', command=self.search)

        self.filemenu1 = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='编辑', menu=self.filemenu1)
        self.filemenu1.add_command(label='新建词条', command=self.new_entry)
        self.filemenu1.add_command(label='删除词条', command=self.delete_entry)
        self.filemenu1.add_cascade(label='撤销', command=self.undo)
        self.filemenu1.add_cascade(label='重做', command=self.redo)

        self.window.config(menu=self.menubar)


    def login(self):
        # 登入页面，确认打开哪一个文件

        print("login in process")

        loginWindow = tk.Tk()
        loginWindow.title("请选择要打开的Json文件")
        loginWindow.geometry("800x300")

        tempLabel00 = tk.Label(loginWindow, font=('Arial', 16))
        tempLabel00.config(text="请输入想要打开的文件名,请在末尾包含“.json”后缀，并保证对象位于同一级目录。")
        tempLabel00.pack(side='top')

        tempLabel01 = tk.Label(loginWindow, font=('Arial', 16))
        tempLabel01.config(text="如文件名不存在，将被创建。")
        tempLabel01.pack(side='top')

        loginEntry = tk.Entry(loginWindow, font=('Arial', 12))
        loginEntry.pack(side='top')


        def login_confirm():
            filename = loginEntry.get()
            if filename is not None and ".json" in filename[-5:]:
                self.path = filename
                self.islogin = True
                loginWindow.destroy()
            else:
                tk.messagebox.showerror("错误", "文件名不能为空")

        loginButton0 = tk.Button(loginWindow, text='确定', command=login_confirm)
        loginButton0.pack(side='top')

        tempLabel1 = tk.Label(loginWindow, font=('Arial', 16), text="或者从浏览器页面选择要打开的文件")
        tempLabel1.pack(side='top')


        def login_confirm_filediag():
            self.path = tk.filedialog.askopenfilename()
            self.islogin = True
            loginWindow.destroy()

        loginButton1 = tk.Button(loginWindow, text='从浏览器页面选择', command=login_confirm_filediag)
        loginButton1.pack(side='top')

        loginWindow.mainloop()


    def loadJson(self):
        # 读取json文件，或新建一个

        # 原文件存在
        try:
            f = open(self.path, 'r')
            self.load = json.load(f)
            f.close()

        # 原文件不存在
        except:
            f = open(self.path, 'w')
            jsondata = '{"dummy":"None" }'
            f.write(jsondata)
            f.close()
            f = open(self.path, 'r')
            self.load = json.load(f)
            f.close()

        # print("The whole loaded content is ", self.load)
        # print("The data type of the variable self.loaded is ", type(self.load))


    def updateIndex(self):
        # 更新self.index和self.indexStrObj
        self.index = list(self.load.keys())
        self.indexStrObj.set( listToString( self.index ) )


    def edit_content(self):
        # 弹出对话框获取词条内容（以TEXT的形式）
        tempWindow = tk.Tk()
        tempWindow.title("请输入词条的新内容")
        tempWindow.geometry('800x300')

        textBar = tk.Text(tempWindow)
        textBar.config(font=('Arial', 12), width=600, height=10)  # 分开写，防止返回None或报错

        tempScroll = tk.Scrollbar(tempWindow, command=textBar.yview)
        textBar.config(yscrollcommand=tempScroll.set)

        def save_the_content():
            # 把改动保存到self.load中

            # 在self.selectedContent被修改之前保存入stack中
            self.undoStack.push(self.selectedEntry, "edit_content", self.selectedContent)

            # 这不是一个“撤销”操作，所以清空redoStack
            self.redoStack.clear()

            # 传值
            self.load[self.selectedEntry] = textBar.get('1.0', 'end')
            self.selectedContent = self.load[self.selectedEntry]

            # print("The info from text bar is: ", self.selectedContent)

            # 注：在保存与退出后更新显示界面，而不是打开“编辑词条内容”后
            self.flag_saved = False
            self.entry_content_changed = True
            self.updatePage()

            # print("The selected Entry is ", self.selectedEntry)
            # print("Its content has been modified, the modified version is: ")
            # print(self.selectedContent)

            self.captionText.set('内容成功编辑！编辑的词条为： ' + self.selectedEntry)

            tempWindow.destroy()

        buttonOK = tk.Button(tempWindow, text="确定并退出", command=save_the_content)

        buttonOK.pack(side='bottom')
        textBar.pack(side='top')
        tempScroll.pack(side="right", fill=tk.Y)


    def new_selection(self, event=None):
        # 为了避免takes 1 para but 2 were given的错误，造一个无用的event充数
        try:
            temp = self.showIndex.curselection()[0] # from a tuple
            print('临时参数temp=self.showIndex.curselection()为： ', temp)

            self.selectedEntry = self.showIndex.get(temp)
            print("选中的self.selectedEntry为： ", self.selectedEntry)

            self.selectedContent = self.load[self.selectedEntry]

            self.curse_selection_changed = True

            self.updatePage()
            self.captionText.set('现在选中的词条为： ' + self.selectedEntry)

        except:
            temp = self.showIndex.curselection()
            print('临时参数temp=self.showIndex.curselection()为： ', temp)


    def new_entry(self):
        # 弹出对话框获取新的词条名，创建一个空白词条,并且将它选中
        # 初始化临时窗口
        tempWindow = tk.Tk()
        tempWindow.title("请输入新词条的名称")
        tempWindow.geometry('300x200')

        # 获取文本输入
        new_entry_bar = tk.Entry(tempWindow, text='请输入')
        new_entry_bar.pack()

        def confirm_new_entry():

            new_entry_get = new_entry_bar.get()

            if new_entry_get not in self.load.keys():

                self.flag_saved = False

                self.load[new_entry_get] = ""

                self.updateIndex()

                # 将新词条选中
                if self.selectedEntry in self.index:
                    self.showIndex.select_clear(self.index.index(self.selectedEntry))
                self.selectedEntry = new_entry_get
                self.selectedContent = self.load[self.selectedEntry]
                self.showIndex.select_set(-1)

                self.curse_selection_changed = True

                # print("variable self.selectedEntry and self.selectedContent have been updated.")

                # 处理Stack
                self.undoStack.push(self.selectedEntry, "new_entry", None)
                # 这不是一个“撤销”操作，所以清空redoStack
                self.redoStack.clear()

                tempWindow.destroy()
                self.updatePage()

                self.captionText.set('新词条创建成功！ 新词条为： ' + self.selectedEntry)
            else:
                print('error: 词条已存在')
                tempWindow.destroy()
                self.captionText.set('错误：词条已存在或名称不符合规范')

        buttomOK = tk.Button(tempWindow, text="确定", command=confirm_new_entry)
        buttomOK.pack(side='bottom')


    def save(self):
        # 保存改动到文件并将flag设为真；将会清空两个用于撤销和重做的Stack
        f = open(self.path, 'w')
        json.dump(self.load, f)
        f.close()
        print("New saved data is ", self.load)

        self.flag_saved = True

        self.updatePage()

        # 清空Stack
        self.undoStack.clear()
        self.redoStack.clear()

        self.captionText.set('内容已经成功保存！ 现在选中的词条为： ' + self.selectedEntry)


    def search(self):
        # 搜索一个词条
        # 弹出对话框获取词条名
        # 初始化临时窗口
        tempWindow = tk.Tk()
        tempWindow.title("请输入需要搜索的词条的名称")
        tempWindow.geometry('300x200')

        # 获取文本输入
        entry_to_search_bar = tk.Entry(tempWindow, text='请输入')
        entry_to_search_bar.pack()

        def do_the_search():

            entry_to_search = entry_to_search_bar.get()

            if entry_to_search in self.load.keys():

                # 将词条选中
                if self.selectedEntry in self.index:
                    self.showIndex.select_clear(self.index.index(self.selectedEntry))
                self.selectedEntry = entry_to_search
                self.selectedContent = self.load[self.selectedEntry]
                self.showIndex.select_set(self.index.index(entry_to_search))

                print("Screens have been updated.")

                self.curse_selection_changed = True

                tempWindow.destroy()
                self.updatePage()

                self.captionText.set('搜索成功！ 现在选中的词条为： ' + self.selectedEntry)
            else:
                print('error: 词条不存在')
                tempWindow.destroy()
                self.captionText.set('错误：词条不存在或名称不符合规范；现在没有词条被选中')
                self.selectedEntry = None
                self.selectedContent = None
                self.updatePage()

        buttomOK = tk.Button(tempWindow, text="确定", command=do_the_search)
        buttomOK.pack(side='bottom')


    def updatePage(self):
        # 更新显示界面的文本和标题
        try:

            # 文本
            if self.entry_content_changed is True:
                self.showText.config(state=tk.NORMAL)
                self.showText.delete('1.0','end')
                self.showText.insert('end', self.selectedContent)
                self.showText.config(state=tk.DISABLED) # 改回不可编辑的状态
                self.entry_content_changed = False

            if self.curse_selection_changed is True:
                self.showText.config(state=tk.NORMAL)
                self.showText.delete('1.0', 'end')
                self.showText.insert('end', self.selectedContent)
                self.showText.config(state=tk.DISABLED)  # 改回不可编辑的状态
                self.curse_selection_changed = False

            # 标题
            if self.flag_saved is False:
                self.window.title("DataBase V4.0 * (未保存)")
            else:
                self.window.title("DataBase V4.0")

            # “撤销”
            if self.undoStack.is_empty():
                self.filemenu1.entryconfig('撤销', state=tk.DISABLED)
            else:
                self.filemenu1.entryconfig('撤销', state=tk.NORMAL)

            # “重做”
            if self.redoStack.is_empty():
                self.filemenu1.entryconfig('重做', state=tk.DISABLED)
            else:
                self.filemenu1.entryconfig('重做', state=tk.NORMAL)

        except:
            print("exception: update is invalid or unnecessary.")


    def delete_entry(self):

        if self.selectedEntry is "":
            print("Deletion is invalid!")
            return None

        tempConfirm = tk.messagebox.askokcancel("请再次确认", "确定要删除选中的词条： " + self.selectedEntry + " 吗？")

        if tempConfirm is True:

            # 先处理Stack
            self.undoStack.push(self.selectedEntry, "delete_entry", self.load[self.selectedEntry])

            # 这不是一个“撤销”操作，所以清空redoStack
            self.redoStack.clear()

            del self.load[self.selectedEntry]

            self.selectedEntry = ""
            self.selectedContent = ""

            self.flag_saved = False
            self.curse_selection_changed = True

            self.updateIndex()
            self.updatePage()
            self.captionText.set("成功删除！现在没有选中的词条。")



    def undo(self):

        self.flag_saved = False

        toDo = self.undoStack.pop()

        if toDo is None:
            return None

        if toDo.op is "edit_content":

            # 先处理另一个Stack
            self.redoStack.push(toDo.name, toDo.op, self.load[toDo.name])

            self.selectedEntry = toDo.name
            self.selectedContent = toDo.content
            self.load[self.selectedEntry] = self.selectedContent

            self.showIndex.select_set(self.index.index(self.selectedEntry))

            self.entry_content_changed = True

            self.updatePage()
            self.captionText.set("撤销编辑内容！目前选中的词条是 ：" + self.selectedEntry)

        elif toDo.op is "new_entry":

            self.redoStack.push(toDo.name, "delete_entry", self.load[toDo.name])

            del self.load[toDo.name]

            self.selectedEntry = ""
            self.selectedContent = ""

            self.curse_selection_changed = True

            self.updateIndex()
            self.updatePage()
            self.captionText.set("成功删除！现在没有选中的词条。")

        elif toDo.op is "delete_entry":

            self.redoStack.push(toDo.name, "new_entry", None)

            self.load[toDo.name] = toDo.content

            # 将新词条选中
            if self.selectedEntry in self.index:
                self.showIndex.select_clear(self.index.index(self.selectedEntry))
            self.selectedEntry = toDo.name
            self.selectedContent = self.load[self.selectedEntry]
            self.showIndex.select_set(-1)

            self.curse_selection_changed = True

            self.updateIndex()
            self.updatePage()
            self.captionText.set('新词条创建成功！ 新词条为： ' + self.selectedEntry)


    def redo(self):

        self.flag_saved = False

        toDo = self.redoStack.pop()

        if toDo is None:
            return None

        if toDo.op is "edit_content":

            # 先处理另一个Stack
            self.undoStack.push(toDo.name, toDo.op, self.load[toDo.name])

            self.selectedEntry = toDo.name
            self.selectedContent = toDo.content
            self.load[self.selectedEntry] = self.selectedContent

            self.showIndex.select_set(self.index.index(self.selectedEntry))

            self.entry_content_changed = True

            self.updatePage()
            self.captionText.set("重做编辑内容！目前选中的词条是 ：" + self.selectedEntry)

        elif toDo.op is "new_entry":

            self.undoStack.push(toDo.name, "delete_entry", self.load[toDo.name])

            del self.load[toDo.name]

            self.selectedEntry = ""
            self.selectedContent = ""

            self.curse_selection_changed = True

            self.updateIndex()
            self.updatePage()
            self.captionText.set("成功删除！现在没有选中的词条。")

        elif toDo.op is "delete_entry":

            self.undoStack.push(toDo.name, "new_entry", None)

            self.load[toDo.name] = toDo.content

            # 将新词条选中
            if self.selectedEntry in self.index:
                self.showIndex.select_clear(self.index.index(self.selectedEntry))
            self.selectedEntry = toDo.name
            self.selectedContent = self.load[self.selectedEntry]
            self.showIndex.select_set(-1)

            self.curse_selection_changed = True

            self.updateIndex()
            self.updatePage()
            self.captionText.set('新词条创建成功！ 新词条为： ' + self.selectedEntry)



# 运行
if __name__ == "__main__":
    dataEditor = DataEditor()
    dataEditor.window.mainloop()


