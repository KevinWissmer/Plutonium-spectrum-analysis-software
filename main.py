import tkinter as tk

test_text = 'unberührt'


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def say_hi(self):
        global session_storage

        print(session_storage.text)




def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb

class Application2(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.window =None
        self.pack()
        self.create_btn()
        self.create_widgets()

    def create_widgets(self):
        self.window = tk.Frame(self.master, bg='#8f8f8f', width=200, height=200)
        self.window.pack(side='right', padx='15', pady='5')
        self.window.pack_propagate(0)


        #Application(master=subFrame_mainFrame2)

    def create_btn(self):
        self.hi_there = tk.Button(self.master)
        self.hi_there["text"] = "(click me)"
        self.hi_there["command"] = self.changetesttext
        self.hi_there.pack(side="top")

    def changetesttext(self):
        global session_storage
        session_storage.text = 'changed'

class SessionStorage():
    def __init__(self):
        self.text= None


root = tk.Tk()
root.geometry("1200x600")

session_storage = SessionStorage()

mainFrame_info = tk.Frame(master=root , bg='#444', width = 500, height = 100)
mainFrame_info.pack()
mainFrame_info.pack_propagate(0)

mainFrame_function = tk.Frame(master=root , bg='#333', width = 500, height = 300)
mainFrame_function.pack()
mainFrame_function.pack_propagate(0)

subFrame_mainFrame1 = tk.Frame(mainFrame_function, bg='#8f8f8f', width=200, height=200)
subFrame_mainFrame1.pack(side='left', padx='15', pady='5')
subFrame_mainFrame1.pack_propagate(0)



app = Application(master=subFrame_mainFrame1)
app = Application2(master=mainFrame_function)


app.mainloop()