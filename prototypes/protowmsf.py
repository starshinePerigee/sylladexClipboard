"""comitting to individual shaped frames this time - it seems to support
our objectives best and is the easiest implimentation, despite being
a bit weird of an approach?"""

from time import sleep
import wx

IMAGE_PATH = r"C:\Users\McGiffenK\Desktop\testpy\sylladex\prototypes\card.png"
FRAMES = 6
OFFSET = 30  # 30
CARDSPACE = 50  # 50
TIMESTEP = 120
STARTPOINT = 100


def screenModulo(point):
    return wx.Point(point[0] % wx.DisplaySize()[0],
                    point[1] % wx.DisplaySize()[1])


class SylladexCard(wx.MiniFrame):
    """an individual card, with display representation

    https://stackoverflow.com/questions/4873063/what-is-the-simplest-way-to-create-a-shaped-window-in-wxpython
    """
    # TODO: add separate "update image from placeholder" method
    runningID = 0

    def __init__(self, parent=None, x=0, y=0, bmp=None):
        self.ID = SylladexCard.runningID
        SylladexCard.runningID += 1
        wx.Frame.__init__(self, parent=parent, id=self.ID,
                          title=f"Sylladex Card {str(self.ID)}",
                          style=wx.FRAME_SHAPED |
                          wx.SIMPLE_BORDER |
                          wx.STAY_ON_TOP |
                          wx.FRAME_NO_TASKBAR)

        if bmp:
            self.bmp = bmp
        else:
            image = wx.Image(IMAGE_PATH, wx.BITMAP_TYPE_PNG)
            self.bmp = wx.Bitmap(image)
        self.SetClientSize((self.bmp.GetWidth(), self.bmp.GetHeight()))
        self.SetShape(wx.Region(self.bmp))
        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)

        self.Bind(wx.EVT_PAINT, self.onPaint)

        self.alpha = 0
        self.coords = wx.Point(x, y)

        self.fadeIn(wx.Point(x, y))

    def fadeIn(self, endpoint):
        self.coords = wx.Point(endpoint.x - OFFSET,
                               endpoint.y - OFFSET)
        self.alpha = 0
        self.SetTransparent(self.alpha)

        self.Show()
        self.fadeMove(endpoint, 255)

    def fadeMove(self, endpoint=None, transparency=255):
        """move smoothly from the current position and transparency to
        the target position and transparency"""

        self.Move(screenModulo(self.coords))  # re-home the window
        if endpoint is None or endpoint == self.coords:
            doMove = False
        else:
            doMove = True
            startpoint = wx.RealPoint(self.coords.x, self.coords.y)
            endpoint = wx.Point(endpoint)
            dX = (endpoint.x - startpoint.x) / FRAMES
            dY = (endpoint.y - startpoint.y) / FRAMES
            self.coords = endpoint
            # print(f"Moving from {str(startpoint)} to {str(endpoint)} at a " +
            #       f"rate of ({str(dX)}, {str(dY)})")

        self.SetTransparent(self.alpha)
        if transparency == self.alpha:
            doAlpha = False
        else:
            doAlpha = True
            startAlpha = float(self.alpha)
            dA = (transparency - startAlpha) / FRAMES
            self.alpha = transparency
            # print(f"Fading from {str(startAlpha)} to {str(transparency)} at " +
            #       f"a rate of {str(dA)}")

        if not (doMove or doAlpha):
            return

        # the more frames, the slower to move.
        for __ in range(0, FRAMES):
            sleep(1/TIMESTEP)
            if doMove:
                startpoint.x += dX
                startpoint.y += dY
                self.Move(screenModulo(startpoint))

            if doAlpha:
                startAlpha += dA
                self.SetTransparent(int(startAlpha))

            self.Update()

    def drawX(self, evt=None):
        pass

    def onPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)
        dc.DrawText(str(self.ID), 20, 20)

    def onExit(self, evt=None):
        self.fadeMove(self.coords-(0, OFFSET), 0)
        self.Destroy()


class MainFrame(wx.Frame):
    """the top level window that manages the program"""

    def __init__(self):
        wx.Frame.__init__(self, None, title='Main Frame', size=(800, 600))

        self.Bind(wx.EVT_CLOSE, self.OnExit)

        self.initializeGUI()

        self.deck = []

        self.Show()

    def initializeGUI(self):
        panel = wx.Panel(self)
        mySizer = wx.BoxSizer(wx.VERTICAL)

        self.testCtrl = wx.TextCtrl(panel)
        mySizer.Add(self.testCtrl, 0, wx.ALL | wx.EXPAND, 5)

        myBtn = wx.Button(panel, label='Press Me', pos=(5, 55))
        myBtn.Bind(wx.EVT_BUTTON, self.onPress)
        mySizer.Add(myBtn, 0, wx.ALL | wx.CENTER, 5)

        addBtn = wx.Button(panel, label="Add Card")
        addBtn.Bind(wx.EVT_BUTTON, self.addCard)
        mySizer.Add(addBtn, 0, wx.ALL | wx.CENTER, 5)

        dropBtn = wx.Button(panel, label="Drop Card")
        dropBtn.Bind(wx.EVT_BUTTON, self.dropCard)
        mySizer.Add(dropBtn, 0, wx.ALL | wx.CENTER, 5)

        invalidBtn = wx.Button(panel, label="Invalid Card")
        invalidBtn.Bind(wx.EVT_BUTTON, self.invalidCard)
        mySizer.Add(invalidBtn, 0, wx.ALL | wx.CENTER, 5)

        resetBtn = wx.Button(panel, label="Reset Sylladex")
        resetBtn.Bind(wx.EVT_BUTTON, self.resetCards)
        mySizer.Add(resetBtn, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(mySizer)

    def onPress(self, event):
        value = self.testCtrl.GetValue()
        if not value:
            print("You didn't enter anything!")
        else:
            print(f'You typed: "{value}"')

    def addCard(self, event=None):
        try:
            count = int(self.testCtrl.GetValue())
        except ValueError:
            count = 1

        for __ in range(0, count):
            coord = len(self.deck) * CARDSPACE + STARTPOINT
            card = SylladexCard(self, coord, coord)
            self.deck.append(card)

    def dropCard(self, event=None):
        card = self.deck.pop(0)
        card.onExit()

        for i, card in enumerate(self.deck):
            card.fadeMove((i*CARDSPACE+STARTPOINT, i*CARDSPACE+STARTPOINT))

    def invalidCard(self, event=None):
        self.deck[len(self.deck)-1].drawX()

    def resetCards(self, event=None):
        for card in self.deck:
            card.onExit()
        self.deck.clear()

    def OnExit(self, evt=None):
        for card in self.deck:
            card.onExit()
        self.Destroy()


app = wx.App(False)
frame = MainFrame()
app.MainLoop()
print("Exited successfully.")
