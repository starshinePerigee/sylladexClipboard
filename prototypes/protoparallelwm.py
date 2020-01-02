"""
This prototypes an inner loop for updating multiple card windows all at once.

It should draw pretty heavily from protowmsf.py
"""

from time import sleep, time
import wx

# default image for new cards:
IMAGE_PATH = r"C:\Users\McGiffenK\Desktop\testpy\sylladex\prototypes\card.png"
# offset to use when fading in new cards:
OFFSET = 30
# time duration to fade in a card:
FADE_IN_DURATION = 0.5
# card destruction offset:
DESTROY_OFFSET = wx.Point(0, -100)
# spacing between cards:
CARD_SPACE = 50
# xy location of the first card:
START_POINT = 100


class SylladexCard(wx.MiniFrame):
    """ An individual card drawn on the screen

    https://stackoverflow.com/questions/4873063/what-is-the-simplest-way-to-create-a-shaped-window-in-wxpython

    Eventually this will also have data, a picture, etc... but since you're in
    "Protoparallelwm.py" you get what you came here for xp
    """

    runningID = 0

    @classmethod
    def screenModulo(cls, point):
        """return a point constrained to the current display size"""
        ds = wx.DisplaySize()
        return wx.Point(point[0] % ds[0], point[1] % ds[1])

    def __init__(self, parent=None, x=0, y=0, bmp=None):
        """create a new card"""
        self.ID = SylladexCard.runningID
        SylladexCard.runningID += 1

        self.pos = wx.Point(x, y)
        self.startTime = None
        self.endTime = None
        self.alpha = 0
        self.startAlpha = None
        self.endAlpha = None
        self.startPos = None
        self.endPos = None
        self.live = False
        self.destroy = False
        self.hidden = True

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

        self.fadeIn(wx.Point(x, y))

    def fadeIn(self, endpoint):
        """set position, transparency, and time variables to fade in a card
        on first call."""
        self.pos = wx.Point(endpoint.x - OFFSET,
                            endpoint.y - OFFSET)
        self.startPos = self.pos
        self.endPos = endpoint

        self.alpha = 0
        self.startAlpha = 0
        self.endAlpha = 255

        self.startTime = time()
        self.endTime = self.startTime + FADE_IN_DURATION

        self.live = True
        self.tick()

    def tick(self):
        """update position and transparency of card based on
        time and target position"""

        if not self.live:
            return

        currentTime = time()
        if currentTime >= self.endTime:
            if self.destroy:
                print(f"Destroying window {self.ID}")
                self.Destroy()
                return
            self.live = False
            self.alpha = self.endAlpha
            self.startAlpha = self.endAlpha
            self.pos = self.endPos
            self.startPos = self.endPos
        else:
            interp = ((currentTime - self.startTime) /
                      (self.endTime - self.startTime))

            self.alpha = self.startAlpha + ((self.endAlpha - self.startAlpha)
                                            * interp)
            self.pos = self.startPos + ((self.endPos - self.startPos)
                                        * interp)

        self.SetTransparent(int(self.alpha))
        self.Move(SylladexCard.screenModulo(self.pos))

        if self.hidden:
            self.hidden = False
            self.Show()

        self.Update()


    def startMoveFade(self, endPoint=None, endAlpha=None, duration=1):
        """order this card to move to a position or fade to an alpha value"""
        if not (endPoint or endAlpha):
            return

        if endPoint:
            self.endPos = endPoint

        if endAlpha:
            self.endAlpha = endAlpha

        self.startTime = time()
        self.endTime = self.startTime + duration
        self.live = True

    def setMoveFade(self, endPoint=None, endAlpha=None):
        """instantly set position and alpha"""

        self.startTime = None
        self.endTime = None
        self.live = False

        if not (endPoint or endAlpha):
            return

        if endPoint:
            self.endPos = endPoint
            self.pos = self.endPos
            self.startPos = self.endPos

        if endAlpha:
            self.alpha = self.endAlpha
            self.startAlpha = self.endPos
            self.endAlpha = endAlpha

        self.Update()

    def drawX(self, evt=None):
        pass

    def remove(self):
        self.destroy = True
        self.startMoveFade(self.pos+DESTROY_OFFSET, 0, 0.3)

    def onPaint(self, evt):
        """WX event to redraw the contents of the window
        https://wxpython.org/Phoenix/docs/html/wx.PaintEvent.html
        """
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)
        dc.DrawText(str(self.ID), 20, 20)

    def onExit(self, evt=None):


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

        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer = wx.Timer(self)
        self.timer.Start(20)

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

        print(f"Adding a card. There are now {len(self.deck)} " +
              "cards in the deck.")
        for __ in range(0, count):
            coord = len(self.deck) * CARD_SPACE + START_POINT
            card = SylladexCard(self, coord, coord)
            self.deck.append(card)

    def dropCard(self, event=None):
        card = self.deck.pop(0)
        card.onExit()

        for i, card in enumerate(self.deck):
            endpoint = wx.Point(i * CARD_SPACE + START_POINT,
                                i * CARD_SPACE + START_POINT)
            card.startMoveFade(endpoint, 255, 0.5)

        print(f"Removing a card. There are currently {len(self.deck)} " +
              "cards in the deck.")

    def invalidCard(self, event=None):
        self.deck[len(self.deck)-1].drawX()

    def resetCards(self, event=None):
        for card in self.deck:
            card.onExit()
        self.deck.clear()

    def OnExit(self, evt=None):
        self.timer.Stop()
        for card in self.deck:
            card.onExit()
        self.Destroy()

    def onTimer(self, event):
        for card in self.deck:
            card.tick()


app = wx.App(False)
frame = MainFrame()
app.MainLoop()
print("Exited successfully.")
