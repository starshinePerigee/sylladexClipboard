import wx
import math
import random


class Bubble(object):
    def __init__(self, x, y, death_size=25, color="GREEN", grow_speed=0.2):
        self.x = x
        self.y = y
        self.radius = 5
        self.death_size = death_size
        self.color = color
        self.grow_speed = grow_speed

    def go(self, bubbles):
        growth = math.log(self.radius) * self.grow_speed
        self.radius = self.radius + growth
        if self.radius >= self.death_size:
            bubbles.remove(self)

    def draw(self, dc, bubbles):
        dc.SetPen(wx.Pen(self.color, 2))
        dc.DrawCircle(self.x, self.y, self.radius)
        self.go(bubbles)



class BubblePanel(wx.Window):
    def __init__(self, parent):
        wx.Window.__init__(self, parent)
        self.bubbles = []
        self.marks = []
        self.last_pos = self.ScreenToClient(wx.GetMousePosition())
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour("WHITE")

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        self.Bind(wx.EVT_CHAR, self.on_character)

        wx.FutureCall(200, self.SetFocus)


    def on_size(self, event):
        width, height = self.GetClientSize()
        self._buffer = wx.EmptyBitmap(width, height)
        self.update_drawing()

    def update_drawing(self):
        self.Refresh(False)

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        x, y = self.ScreenToClient(wx.GetMousePosition())
        self.draw_x(dc, x, y, 4)
        for bubble in self.bubbles:
            bubble.draw(dc, self.bubbles)
        self.draw_marks(dc)

    def draw_x(self, dc, x, y, line_width):
        dc.SetPen(wx.Pen("BLACK", line_width))
        dc.DrawLine(x-5, y-5, x+5, y+5)  # \
        dc.DrawLine(x-5, y+5, x+5, y-5)  # /

    def draw_marks(self, dc):
        chains = {}
        for (letter, x, y) in self.marks:
            self.draw_x(dc, x, y, 2)
            dc.DrawText(letter, x-3, y-28)
            chains.setdefault(letter, []).append(wx.Point(x,y))
        for (key, points) in chains.items():
            if len(points) > 1:
                if key == key.upper() or len(points) == 2:
                    dc.DrawLines(points)
                else:
                    dc.DrawSpline(points)

    def on_motion(self, event):
        x, y = event.GetPosition()
        motion_score = (abs(x - self.last_pos.x) + abs(y - self.last_pos.y))
        self.last_pos = wx.Point(x, y)
        if random.randint(0, motion_score) > 5:
            self.bubbles.append(Bubble(x, y))
            if random.randint(0, 100) == 0:
                self.bubbles.append(
                    Bubble(x, y, color="PURPLE", death_size=100, grow_speed=0.5))


    def on_left_up(self, event):
        self.bubbles.append(Bubble(event.GetX(), event.GetY(),
                             color="YELLOW", death_size=50, grow_speed=0.1))

    def on_right_up(self, event):
        self.bubbles.append(Bubble(event.GetX(), event.GetY(),
                             color="BLUE", death_size=80, grow_speed=0.6))

    def on_character(self, event):
        key = event.GetKeyCode()
        if key==27:   # Esc key
            self.marks = []
        else:
            x, y = self.ScreenToClient(wx.GetMousePosition())
            self.marks.append( (chr(event.GetKeyCode()), x, y) )



class BubbleFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_TIMER, self.on_timer)

        self.panel = BubblePanel(self)
        self.timer = wx.Timer(self)
        self.timer.Start(20)


    def on_close(self, event):
        self.timer.Stop()
        self.Destroy()

    def on_timer(self, event):
        self.panel.update_drawing()


app = wx.App(False)
frame = BubbleFrame(None, -1, "Bubbles!")
frame.Show(True)
app.MainLoop()
