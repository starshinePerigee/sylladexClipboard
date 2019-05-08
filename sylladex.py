""" SYLLADEX CLIPBOARD MANAGER:
    ~~~MAYBE NOT THE LITERALLY WORST IDEA~~~

Version 0.00.01 THIS IS STUPID

this is the main funciton, numpnuts

what ARE YOU evein DOING

8^Y
"""

import tkinter as tk
import threading


class App(threading.Thread):
    def __init__(self, tk_root):
        self.root = tk_root
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        loop_active = True
        while loop_active:
            user_input = input("Give me your command! Just type \"exit\" to close: ")
            if user_input == "exit":
                loop_active = False
                self.root.quit()
                self.root.update()
            else:
                label = tk.Label(self.root, text=user_input)
                label.pack()


ROOT = tk.Tk()
APP = App(ROOT)
LABEL = tk.Label(ROOT, text="Hello, world!")
LABEL.pack()
ROOT.mainloop()


#
# root = tk.Tk()
#
# root.geometry('200x200+100+100')
# root.resizable(False, False)
# root.overrideredirect(True)
# root.update_idletasks()
# root.mainloop()
