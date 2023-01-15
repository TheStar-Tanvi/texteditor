from tkinter import Tk, Text, Scrollbar, Menu, messagebox, filedialog, Checkbutton, Label, Entry, Frame
import os
from tkinter import messagebox
from tkinter import *
from tkinter.simpledialog import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter.colorchooser import askcolor
from tkinter.font import Font, families
from tkinter.scrolledtext import *


isactive=0

class Editor():
    
    def __init__(self, root):
        self.root = root        
        self.TITLE = "Project Editor"
        self.file_path = None
        self.set_title()
        frame = Frame(root)
        self.yscrollbar = Scrollbar(frame, orient="vertical")
        self.editor = Text(frame, yscrollcommand=self.yscrollbar.set)
        self.editor.pack(side="left", fill="both", expand=1)
        self.editor.config( wrap = "word", # use word wrapping
                undo = True, # Tk 8.4 
                width = 80 )        
        self.editor.focus()
        self.yscrollbar.pack(side="right", fill="y")
        self.yscrollbar.config(command=self.editor.yview)        
        frame.pack(fill="both", expand=1)
        #instead of closing the window, execute a function
        self.root.protocol("WM_DELETE_WINDOW", self.exit) 
        isactive=False
        self.menubar=Menu(root)
        self.filemenu=Menu(self.menubar,tearoff=0)

        # filemenu
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.filemenu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        self.filemenu.add_command(label="Save", command=self.save_file,  accelerator="Ctrl+S")
        self.filemenu.add_command(label="Save As", command=self.file_save_as,accelerator="Ctrl+Shift+S")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.exit)

        # editmenu
        self.editmenu=Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)
       
        self.editmenu.add_command(label="Cut", state="disabled",command=self.cut,accelerator="Ctrl+X")
        self.editmenu.add_command(label="Copy", state="disabled",command=self.copy, accelerator="Ctrl+C")
        self.editmenu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        self.editmenu.add_command(label="Undo", state="disabled",command=self.undo, accelerator="Ctrl+Z")
        self.editmenu.add_command(label="Redo", state="disabled",command=self.redo, accelerator="Ctrl+R")
        self.editmenu.add_command(label="Find", command=self.find, accelerator="Ctrl+F")
        self.editmenu.add_command(label="Font", command=self.font)
        self.editmenu.add_command(label="Select All", command=self.selectall, accelerator="Ctrl+A")
        self.editmenu.add_command(label="Replace", command=self.replace,accelerator="Ctrl+P")

        # colormenu
        self.colormenu=Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label="Color", menu=self.colormenu)
        self.colormenu.add_command(label="Background_Color",accelerator="Ctrl+Shift+B", command=self.background)
        self.colormenu.add_command(label="Foreground_Color", accelerator="Ctrl+Shift+F",command=self.foreground)


        # executemenu
        self.executemenu=Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label="Execute", menu=self.executemenu)
        self.executemenu.add_command(label="Run", command=self.runfile,accelerator="Ctrl+Shift+R")

        # display the menu
        root.config(menu=self.menubar)

    #file menu functions
    def save_if_modified(self, event=None):
        if self.editor.edit_modified():
            response = messagebox.askyesnocancel("Save?", "This document has been modified. Do you want to save changes?") #yes = True, no = False, cancel = None
            if response:
                result = self.save_file()
                if result == "saved": 
                    return True
                else:
                    return None
            else:
                return response 
        else: 
            return True


    def new_file(self,event=None):
        result = self.save_if_modified()
        if result != None: 
            self.editor.delete(1.0, "end")
            self.editor.edit_modified(False)
            self.editor.edit_reset()
            self.file_path = None
            self.set_title()      

    def open_file(self, event=None, filepath=None):
        result = self.save_if_modified()
        if result != None: 
            if filepath == None:
                filepath = filedialog.askopenfilename()
            if filepath != None  and filepath != '':
                fileContents = open(filepath,'r')
                self.editor.delete(1.0, "end")
                self.editor.insert(1.0, fileContents)
                self.editor.edit_modified(False)
                self.file_path = filepath
                self.set_title()

    def save_file(self,event=None):
        if self.file_path == None:
            result = self.file_save_as()
        else:
            result = self.file_save_as(filepath=self.file_path)
        return result
    

    def file_save_as(self, event=None, filepath=None):
        if filepath == None:
            filepath = filedialog.asksaveasfilename(filetypes=(('Text files', '*.txt'), ('Python files', '*.py *.pyw'), ('All files', '*.*'))) #defaultextension='.txt'
        try:
            with open(filepath, 'wb') as f:
                text = self.editor.get(1.0, "end-1c")
                f.write(bytes(text, 'UTF-8'))
                self.editor.edit_modified(False)
                self.file_path = filepath
                self.set_title()
                return "saved"
        except FileNotFoundError:
            print('FileNotFoundError')
            return "cancelled"
    
    def exit(self, event=None):
        result = self.save_if_modified()
        if result != None: 
            self.root.destroy()

    def set_title(self,event=None):
        if self.file_path != None:
            title = os.path.basename(self.file_path)
        else:
            title = "Untitled"
        self.root.title(title + " - " + self.TITLE)

    # edit menu functions

    def undoredo(self,event):
        self.editmenu.entryconfig("Undo",state="active")
        self.editmenu.entryconfig("Redo",state="active")

    def cutcopy(self,event):
        global isactive
        selection = None
        try:
            selection = self.editor.selection_get()
        except:
            pass

        if selection is not None:
            if isactive:
                self.editmenu.entryconfig("Cut",state="disabled")
                self.editmenu.entryconfig("Copy",state="disabled")
                isactive = False
            else:
                self.editmenu.entryconfig("Cut",state="active")
                self.editmenu.entryconfig("Copy",state="active")
                isactive = True    

    def cut(self,event=None,*args):
        sel=self.editor.selection_get()
        self.clipboard=sel
        self.editor.delete(SEL_FIRST,SEL_LAST)

    def copy(self,event=None,*args):
        sel=self.editor.selection_get()
        self.clipboard=sel

    def paste(self,event=None,*args):
        self.editor.insert(INSERT,self.editor.clipboard_get())
    
    def undo(self,event=None,*args):
        self.editor.edit_undo()

    def redo(self,event=None,*args):
        self.editor.edit_redo()


    def set_mark(self, findString):
        self.find_string(findString)
        self.editor.tag_config('highlight', foreground='red')
        self.editor.focus_force()

    def find_string(self, findString):
        startInd = '1.0'
        while(startInd):
            startInd = self.editor.search(findString, startInd, stopindex=END)
            if startInd:
                startInd = str(startInd)
                lastInd = startInd+f'+{len(findString)}c'
                self.editor.tag_add('highlight', startInd, lastInd)
                startInd = lastInd
   

    def find(self,event=None):
        find_root = Toplevel(self.root)
        find_root.title("Find")
        find_root.transient(self.root)
        find_root.focus_force()
        find_root.grid_columnconfigure(0, weight=1)
        find_root.grid_rowconfigure(0, weight=1)
        e1 = Entry(find_root)
        e1.grid(row=0, column=0, pady="10",
                padx="10", columnspan=4, sticky="EW")

        def sub():
            findString = e1.get()
            self.set_mark(findString)

        def findnext():
            word=e1.get()
            self.editor.tag_remove("match","1.0",END)
            if word:
                start_pos=self.editor.index(INSERT)
                start_pos=self.editor.search(word,start_pos,nocase=1,stopindex=END)
                if not start_pos:return
                end_pos="%s+%dc"%(start_pos,len(word))
                self.editor.tag_add("match",start_pos,end_pos)
                start_pos=end_pos
                self.editor.tag_config("match",foreground="black",background="yellow")


        def findprev():
            word=e1.get()
            self.editor.tag_remove("match","1.0",END)
            if word:
                start_pos=self.editor.index(INSERT)
                start_pos=self.editor.search(word,start_pos,nocase=1,stopindex="1.0",backwards=True)
                if not start_pos:return
                end_pos="%s+%dc"%(start_pos,len(word))
                self.editor.tag_add("match",start_pos,end_pos)
                start_pos=end_pos
                self.editor.tag_config("match",foreground="black",background="cyan")

        def on_closing():
            self.editor.tag_delete('highlight')
            find_root.destroy()

        findBtn = Button(find_root, text="Find", command=sub)
        findnextBtn = Button(find_root, text="Find Next", command=findnext)
        findprevBtn = Button(find_root, text="Find Previous", command=findprev)
        findBtn.grid(row=1, column=0, pady="10", padx="10", sticky="EWS")
        findnextBtn.grid(row=1, column=1, pady="10", padx="10", sticky="EWS")
        findprevBtn.grid(row=1, column=2, pady="10", padx="10", sticky="EWS")
        closeBtn = Button(find_root, text="Close", command=on_closing)
        closeBtn.grid(row=1, column=3, pady="10", padx="10", sticky="EWS")

    def bold(self,*args):
        try:
            current_tags=self.editor.tag_names("sel.first")
            if "bold" in current_tags:
                self.editor.tag_remove("bold", "sel.first", "sel.last")
            else:
                self.editor.tag_add("bold", "sel.first", "sel.last")
                bold_font = Font(self.editor, self.editor.cget("font"))
                bold_font.configure(weight="bold")
                self.editor.tag_configure("bold", font=bold_font)
        except:
            pass

    def italic(self,*args):
        try:
            current_tags = self.editor.tag_names("sel.first")
            if "italic" in current_tags:
                self.editor.tag_remove("italic", "sel.first", "sel.last")
            else:
                self.editor.tag_add("italic", "sel.first", "sel.last")
                italic_font = Font(self.editor, self.editor.cget("font"))
                italic_font.configure(slant="italic")
                self.editor.tag_configure("italic", font=italic_font)
        except:
            pass

    def underline(self,*args):
        try:
            current_tags=self.editor.tag_names("sel.first")
            if "underline" in current_tags:
                self.editor.tag_remove("underline", "sel.first", "sel.last")
            else:
                self.editor.tag_add("underline", "sel.first", "sel.last")
                underline_font = Font(self.editor, self.editor.cget("font"))
                underline_font.configure(underline=1)
                self.editor.tag_configure("underline", font=underline_font)
        except:
            pass
    
    def overstrike(self,*args):
        try:
            current_tags = self.editor.tag_names("sel.first")
            if "overstrike" in current_tags:
                self.editor.tag_remove("overstrike", "sel.first", "sel.last")
            else:
                self.editor.tag_add("overstrike", "sel.first", "sel.last")
                overstrike_font = Font(self.editor, self.editor.cget("font"))
                overstrike_font.configure(overstrike=1)
                self.editor.tag_configure("overstrike", font=overstrike_font)
        except:
            pass

    #font
    def font(self,event=None,*args):
        fontwindow=Toplevel(self.root)
        fontwindow.title("Format")
        fontwindow.resizable(1,0)
        fontwindow.grid_propagate(False)
        fontoptionswdw=Frame(fontwindow)
        fontoptionswdw.pack()


        prev=None
        demo="ABCabc123"
        fontoptions=families(self.root)
        fontsize=[]
        global font_style,font_size
        font_style="Arial"
        font_size=10
        for i in range(8,60,2):
            fontsize.append(i)

        fontstyleLabel=Label(fontoptionswdw,text="Choose Font Style")
        fontstyleLabel.grid(row=0,column=0,padx=5,sticky='W')

        fontstyleLabel = Label(fontoptionswdw,text="Choose Font Size")
        fontstyleLabel.grid(row=0,column=1,sticky='W')

        fontList = Listbox(fontoptionswdw,selectmode="SINGLE",width=40)
        fontList.grid(row=1,column=0,padx=5)
        fontSizeList =Listbox(fontoptionswdw,selectmode="SINGLE",width=40)
        fontSizeList.grid(row=1,column=1)

        italicButton=IntVar()
        boldButton=IntVar()
        underlineButton=IntVar()
        strikeButton=IntVar()

        #font style options
        def selected_item(*args):
            for i in fontList.curselection():
                style = fontList.get(i)
                global font_style
                font_style=style
                font=Font(family=font_style,size=font_size)
                prev.configure(font=font)

        for option in fontoptions:
            fontList.insert('end',option)
        fontList.bind("<<ListboxSelect>>",selected_item)

        #font size options
        def selected_size(*args):
            for i in fontSizeList.curselection():
                size = fontSizeList.get(i)
                global font_size
                font_size=size
                font=Font(family=font_style,size=font_size)
                prev.configure(font=font)

        for option in fontsize:
            fontSizeList.insert('end',option)
        fontSizeList.bind("<<ListboxSelect>>",selected_size)
        
        #italic
        def setitalic(*args):
            try:
                current_tags=prev.tag_names("1.0") #seq of tag names associated with char after passed index (in arg)
                if italicButton:
                    if "italic" in current_tags:
                        prev.tag_remove("italic","1.0",END)
                    else:
                        prev.tag_add("italic","1.0",END)
                        italicfont=Font(prev,prev.cget("font"))
                        italicfont.configure(slant="italic")
                        prev.tag_configure("italic",font=italicfont)
                else:
                    if "italic" in current_tags:
                        prev.tag_remove("italic","1.0",END)
            except Exception as error:
                pass

        #bold 
        def setbold(*args):
            try:
                current_tags=prev.tag_names("1.0") #seq of tag names associated with char after passed index (in arg)
                if boldButton:
                    if "bold" in current_tags:
                        prev.tag_remove("bold","1.0",END)
                    else:
                        prev.tag_add("bold","1.0",END)
                        boldfont=Font(prev,prev.cget("font"))
                        boldfont.configure(weight="bold")
                        prev.tag_configure("bold",font=boldfont)
                else:
                    if "bold" in current_tags:
                        prev.tag_remove("bold","1.0",END)
            except:
                pass


        #underline
        def setunderline(*args):
            try:
                current_tags=prev.tag_names("1.0") #seq of tag names associated with char after passed index (in arg)
                if underlineButton:
                    if "underline" in current_tags:
                        prev.tag_remove("underline","1.0",END)
                    else:
                        prev.tag_add("underline","1.0",END)
                        underlinefont=Font(prev,prev.cget("font"))
                        underlinefont.configure(underline=1)
                        prev.tag_configure("underline",font=underlinefont)
                else:
                    if "underline" in current_tags:
                        prev.tag_remove("underline","1.0",END)
            except:
                pass


        #strike
        def setstrike(*args):
            try:
                current_tags=prev.tag_names("1.0") #seq of tag names associated with char after passed index (in arg)
                if strikeButton:
                    if "overstrike" in current_tags:
                        prev.tag_remove("overstrike","1.0",END)
                    else:
                        prev.tag_add("overstrike","1.0",END)
                        strikefont=Font(prev,prev.cget("font"))
                        strikefont.configure(overstrike=1)
                        prev.tag_configure("overstrike",font=strikefont)
                else:
                    if "overstrike" in current_tags:
                        prev.tag_remove("overstrike","1.0",END)
            except:
                pass


        #apply
        def apply():
            if italicButton:setitalic()
            if boldButton:setbold()
            if underlineButton:setunderline()
            if strikeButton:setstrike()
            textstyle=font_style
            textsize=font_size
            font=Font(family=textstyle,size=textsize)
            self.editor.configure(font=font)

        styleframe=Frame(fontwindow)
        styleframe.pack()
        
        check1=Checkbutton(styleframe,text="Italic",variable=italicButton,onvalue=1,offvalue=0,height=5,width=5)
        check2=Checkbutton(styleframe,text="Bold",variable=boldButton,onvalue=1,offvalue=0,height=5,width=5)
        check3=Checkbutton(styleframe,text="Underline",variable=underlineButton,onvalue=1,offvalue=0,height=5,width=9)
        check4=Checkbutton(styleframe,text="Overstrike",variable=strikeButton,onvalue=1,offvalue=0,height=5,width=11)

        check1.bind('<ButtonRelease-1>',setitalic)
        check2.bind('<ButtonRelease-1>',setbold)
        check3.bind('<ButtonRelease-1>',setunderline)
        check4.bind('<ButtonRelease-1>',setstrike)

        check1.grid(row=0,column=0,sticky='W')
        check2.grid(row=0,column=1,sticky='W')
        check3.grid(row=0,column=2,sticky='W')
        check4.grid(row=0,column=3,sticky='W')

        prevFrame = Frame(fontwindow)
        prevFrame.pack()
        prev = Text(prevFrame,bg="#fff",border="1px solid #",width=30,height=5)
        prev.insert(END,demo)
        prev.grid(row=0,column=0,sticky='N')

        buttonFrame = Frame(fontwindow)
        buttonFrame.pack()
        Button(buttonFrame,bg="#fff",border="1px solid #",text="OK",width=20,command=fontwindow.quit).grid(row=0,column=0,sticky='W',padx=20,pady=20)
        Button(buttonFrame,bg="#fff",border="1px solid #",text="Cancel",width=20,command=fontwindow.quit).grid(row=0,column=1,pady=20)
        Button(buttonFrame,bg="#fff",border="1px solid #",text="Apply",width=20,command=apply).grid(row=0,column=2,sticky='E',padx=20,pady=20)
        fontwindow.mainloop()

    #select all
    def selectall(self,event=None,*args):
        self.editor.tag_add(SEL,"1.0",END)

    # replace
    def replace(self,event=None,*args):
        replace_wdw=Toplevel(self.root)
        replace_wdw.title("Find and Replace")
        replace_wdw.transient(self.root) #transient window
        replace_wdw.focus_force() #Force the input focus to the widget
        e1 = Entry(replace_wdw)
        e1.grid(row=0, column=0, pady=5, columnspan=2, padx=10)
        e2 = Entry(replace_wdw)
        e2.grid(row=1, column=0, pady=5, columnspan=2, padx=10)
        def find():
            findString = e1.get()
            self.set_mark(findString)

        def replace():
            findString = e1.get()
            replaceString = e2.get()
            myText = self.editor.get('1.0', END)
            myText = myText.replace(findString, replaceString)
            self.editor.delete('1.0', END)
            self.editor.insert('1.0', myText)
            replace_wdw.destroy()

        def on_closing():
            self.editor.tag_delete('highlight')
            replace_wdw.destroy()

        findButton = Button(replace_wdw, text="Find", command=find)
        replaceButton = Button(replace_wdw, text="Replace", command=replace)
        findButton.grid(row=2, column=0, padx=10, pady=5)
        replaceButton.grid(row=2, column=1, padx=10, pady=5)
        root.protocol("WM_DELETE_WINDOW", on_closing)

    # color menu functions

    def background(self,event=None,*args):
        hexstr=askcolor(title ="Choose color")
        color=hexstr[1]
        if color:
            self.editor.config(bg=color)

    def foreground(self,event=None,*args):
        hexstr=askcolor(title ="Choose color")
        color=hexstr[1]
        if color:
            self.editor.config(fg=color)

    # execute menu functions

    def runfile(self,event=None,*args):
        if self.file_path=="" or self.file_path is None:
            self.open_file()
        try:
            if self.file_path.split('.')[1]=='py':
                os.system("python3 "+self.file_path)
            else:
                messagebox.showerror("showerror","File not supported")
        except:
            messagebox.showerror("showerror","Couldn't execute file")

        

    def main(self, event=None):   
        self.editor.bind_all("<Control-n>", self.new_file)                       
        self.editor.bind_all("<Control-N>", self.new_file) 
        self.editor.bind_all("<Control-Shift-s>", self.file_save_as)       
        self.editor.bind_all("<Control-Shift-S>", self.file_save_as)       
        self.editor.bind_all("<Control-o>", self.open_file)
        self.editor.bind_all("<Control-O>", self.open_file)
        self.editor.bind_all("<Control-S>", self.save_file)
        self.editor.bind_all("<Control-s>", self.save_file)  
        self.editor.bind_all("<Control-a>", self.selectall)        
        self.editor.bind_all("<Control-A>", self.selectall)        
        self.editor.bind_all("<Control-x>", self.cut)        
        self.editor.bind_all("<Control-X>", self.cut)        
        self.editor.bind_all("<Control-c>", self.copy)        
        self.editor.bind_all("<Control-C>", self.copy)        
        self.editor.bind_all("<Control-v>", self.paste)        
        self.editor.bind_all("<Control-V>", self.paste)        
        self.editor.bind_all("<Control-z>", self.undo)        
        self.editor.bind_all("<Control-Z>", self.undo)        
        self.editor.bind_all("<Control-r>", self.redo)        
        self.editor.bind_all("<Control-R>", self.redo)        
        self.editor.bind_all("<Control-f>", self.find)        
        self.editor.bind_all("<Control-F>", self.find)        
        self.editor.bind_all("<Control-b>", self.bold)        
        self.editor.bind_all("<Control-B>", self.bold)        
        self.editor.bind_all("<Control-i>", self.italic)        
        self.editor.bind_all("<Control-I>", self.italic)        
        self.editor.bind_all("<Control-t>", self.overstrike)
        self.editor.bind_all("<Control-T>", self.overstrike)
        self.editor.bind_all("<Control-f>",self.find)
        self.editor.bind_all("<Control-F>",self.find) 
        self.editor.bind_all("<Control-P>",self.replace)
        self.editor.bind_all("<Control-p>",self.replace)   
        self.editor.bind_all("<Control-Shift-B>",self.background)
        self.editor.bind_all("<Control-Shift-b>",self.background)
        self.editor.bind_all("<Control-Shift-f>",self.foreground)
        self.editor.bind_all("<Control-Shift-f>",self.foreground)
        self.editor.bind_all("<Control-Shift-r>",self.runfile)
        self.editor.bind_all("<Control-Shift-R>",self.runfile)
        self.editor.bind("<Key>",self.undoredo)
        self.editor.bind("<<Selection>>",self.cutcopy)
        self.editor.bind("<Button>",self.cutcopy)
        self.editor.bind_all()
             


root = Tk()
photo=PhotoImage(file="/home/tanvi/Downloads/torcicon.png")
root.iconphoto(True,photo)
editor = Editor(root)
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))
editor.main()
root.mainloop()

