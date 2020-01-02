"""We've never used WX before, so let's play with it a bit!

This app opens some windows, displays some text, dropdowns, and lets you
open some other windows.

https://realpython.com/python-gui-with-wxpython/
https://wxpython.org/Phoenix/docs/html/sizers_overview.html

https://realpython.com/python-f-strings/
"""

import wx

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Hello World')

        panel = wx.Panel(self)
        mySizer = wx.BoxSizer(wx.VERTICAL)

        self.testCtrl = wx.TextCtrl(panel)
        mySizer.Add(self.testCtrl, 0, wx.ALL | wx.EXPAND, 5)

        myBtn = wx.Button(panel, label='Press Me', pos=(5, 55))
        myBtn.Bind(wx.EVT_BUTTON, self.onPress)
        mySizer.Add(myBtn, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(mySizer)

        self.Show()

    def onPress(self, event):
        value = self.testCtrl.GetValue()
        if not value:
            print("You didn't enter anything!")
        else:
            print(f'You typed: "{value}"')


app = wx.App()
frame = MyFrame()
frame.Show()
app.MainLoop()
