import sys
from PySide2 import QtCore, QtWidgets, QtGui

# default image for new cards:
IMAGE_PATH = r"C:\Users\McGiffenK\Desktop\testpy\sylladex\prototypes\card.png"
PUNCHED_PATH = r"C:\Users\McGiffenK\Desktop\testpy\sylladex\prototypes\punched.png"
CROSS_PATH = r"C:\Users\McGiffenK\Desktop\testpy\sylladex\prototypes\cross.png"
# offset to use when fading in new cards:
OFFSET = QtCore.QPoint(50, 50)
OFFSET_DELAY = 0.05
# time duration to fade in a card:
FADE_IN_POSITION = QtCore.QPoint(-30, -30)
FADE_IN_DURATION = 0.5
# card destruction offset:
DESTROY_OFFSET = QtCore.QPoint(0, -100)
DESTROY_DURATION = 0.1
DESTROY_FILL_DURATION = 0.1
DESTROY_FILL_DELAY = 0.05
#
TOGGLE_DELAY = 0.3
TOGGLE_COUNT = 3
# spacing between cards:
CARD_SPACE = 50
# xy location of the first card:
START_POINT = QtCore.QPoint(100, 100)


class CardOverlay(QtWidgets.QLabel):
    def __init__(self, parent, pixmap):
        super(CardOverlay, self).__init__(parent.parent())
        self.setPixmap(pixmap)
        self.move(parent.geometry().center()-pixmap.rect().center())
        z_parent = self.parent().children().index(parent)
        self.stackUnder(self.parent().children()[z_parent+1])

        # not relevant right now but still:
        # https://eli.thegreenplace.net/2011/04/25/passing-extra-arguments-to-pyqt-slot
        self.togglecount = 0
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(int(TOGGLE_DELAY*1000))
        self.timer.timeout.connect(self.toggle)
        self.timer.start()

    def toggle(self):
        self.togglecount += 1
        if self.togglecount > (TOGGLE_COUNT*2-1):
            self.end_toggle()
        else:
            if self.isVisibleTo(self.parent()):
                self.hide()
            else:
                self.show()

    def end_toggle(self):
        self.hide()
        self.deleteLater()


class SylladexCard(QtWidgets.QLabel):
    clicked = QtCore.Signal(str)
    # there is currently an issue where label clickable bounding boxes are
    # rectangles only - this would need to inherit from QGraphicsObject
    # ref https://stackoverflow.com/questions/29372383/qt-mousepressevent-modify-the-clickable-area
    runningID = 0

    def __init__(self, parent=None, startpoint=QtCore.QPoint(0, 0), delay=0.0):
        self.ID = SylladexCard.runningID
        SylladexCard.runningID += 1

        super(SylladexCard, self).__init__(parent)
        self.clicked.connect(self.mousePressEvent)

        self.unpunched = QtGui.QPixmap(IMAGE_PATH)
        self.punched = QtGui.QPixmap(PUNCHED_PATH)
        self.isPunched = False
        self.setPixmap(self.unpunched)

        self.position = startpoint+FADE_IN_POSITION
        self.move(self.position)
        self.move_ani = None

        self.alpha = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.alpha)
        self.alpha.setOpacity(0)
        self.alphaValue = 0
        self.fade_ani = None

        self.IDLabel = QtWidgets.QLabel(str(self.ID), self)
        self.IDLabel.move(15, 18)
        self.IDLabel.show()

        self.fade_animation(1, FADE_IN_DURATION, delay)
        self.move_animation(startpoint, FADE_IN_DURATION, delay)

        self.show()

    @staticmethod
    def arbitrary_animation(animation, oldvalue, newvalue,
                            duration, delay=0.0):
        # http://zetcode.com/pyqt/QtCore.QPropertyAnimation/
        # print(f"moving from {oldvalue} to {newvalue}")
        animation.setDuration((duration + delay) * 1000)
        animation.setKeyValueAt(delay/(duration+delay), oldvalue)
        animation.setStartValue(oldvalue)
        animation.setEndValue(newvalue)
        animation.start()

    # noinspection PyTypeChecker
    def fade_animation(self, new_alpha, duration, delay=0.0):
        self.fade_ani = QtCore.QPropertyAnimation(self.alpha, b"opacity")
        self.arbitrary_animation(self.fade_ani, self.alphaValue, new_alpha,
                                 duration, delay)
        self.alphaValue = new_alpha

    # noinspection PyTypeChecker
    def move_animation(self, new_pos, duration, delay=0.0):
        self.move_ani = QtCore.QPropertyAnimation(self, b"pos")
        self.arbitrary_animation(self.move_ani, self.position, new_pos,
                                 duration, delay)
        self.position = new_pos
        print(f"Card ID {self.ID} is in position {self.position}")

    def delete(self, delay=0):
        self.fade_animation(0.5, DESTROY_DURATION, delay)
        self.move_animation(self.position+DESTROY_OFFSET,
                            DESTROY_DURATION, delay)
        QtCore.QTimer.singleShot(int((delay+DESTROY_DURATION)*1000),
                                 self.deleteLater)

    def flash_invalid(self):
        CardOverlay(self, QtGui.QPixmap(CROSS_PATH))

    def mousePressEvent(self, event):
        if self.isPunched:
            self.setPixmap(self.unpunched)
        else:
            self.setPixmap(self.punched)
        self.isPunched = not self.isPunched
        self.raise_()


class CardDisplay(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(CardDisplay, self).__init__(parent)
        self.setWindowTitle("Sylladex Card Display")
        # set size to fill the screen
        self.setGeometry(self.screen().availableGeometry())

        self.setWindowFlags(self.windowFlags() |
                            QtCore.Qt.Tool |
                            QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.cards = []

        self.show()

    def screen_modulo(self, point):
        ds = self.screen().availableGeometry()
        return(QtCore.QPoint(point.x() % ds.width() + ds.x(),
                             point.y() % ds.height() + ds.y()))

    def add_card(self, count):
        for i in range(0, count):
            self.cards.append(SylladexCard(self, self.screen_modulo(
                    OFFSET*len(self.cards)+START_POINT), i * OFFSET_DELAY))
            print(f"Card added. "
                  f"There are now {len(self.cards)} cards in the display.")

    def drop_card(self, position):
        self.cards.pop(position).delete()
        for i in range(position, len(self.cards)):
            self.cards[i].move_animation(
                    self.screen_modulo(self.cards[i].position-OFFSET),
                    DESTROY_FILL_DURATION,
                    DESTROY_FILL_DELAY*(i-position))
        print(f"Removed card from position {position}, "
              f"there are now {len(self.cards)}.")

    def x_card(self, position):
        self.cards[position].flash_invalid()

    def clear_cards(self):
        for i in range(0, len(self.cards)):
            self.cards[i].delete(DESTROY_FILL_DELAY*i)
        self.cards = []

    def destroy_self(self):
        self.deleteLater()


class MainWindow(QtWidgets.QDialog):
    """The parent window with controls"""
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Sylladex Display Manager Test")

        # create widgets and add to layout:
        layout = QtWidgets.QVBoxLayout()
        self.entryField = QtWidgets.QLineEdit("")
        layout.addWidget(self.entryField)
        self.textButton = QtWidgets.QPushButton("Read Text")
        layout.addWidget(self.textButton)
        self.addCardButton = QtWidgets.QPushButton("Add Card")
        layout.addWidget(self.addCardButton)
        self.dropCardButton = QtWidgets.QPushButton("Drop Card")
        layout.addWidget(self.dropCardButton)
        self.invalidCardButton = QtWidgets.QPushButton("Invalid Card")
        layout.addWidget(self.invalidCardButton)
        self.clearAllButton = QtWidgets.QPushButton("Clear All")
        layout.addWidget(self.clearAllButton)
        self.resetSylButton = QtWidgets.QPushButton("Reset Sylladex")
        layout.addWidget(self.resetSylButton)
        self.breakButton = QtWidgets.QPushButton("Break")
        layout.addWidget(self.breakButton)

        # Set dialog layout
        self.setLayout(layout)

        # initialize display window
        self.display = self.initialize_display()

        # bind buttons
        self.textButton.clicked.connect(self.on_press)
        self.breakButton.clicked.connect(self.on_break)
        self.addCardButton.clicked.connect(self.on_add)
        self.dropCardButton.clicked.connect(self.on_drop)
        self.invalidCardButton.clicked.connect(self.on_invalid)
        self.clearAllButton.clicked.connect(self.on_clear)
        self.resetSylButton.clicked.connect(self.on_reset)

    def initialize_display(self):
        return CardDisplay(self)

    def on_press(self):
        value = self.entryField.text()
        if not value:
            print("You didn't enter anything!")
        else:
            print(f'You typed: "{value}"')

    def on_add(self):
        try:
            value = int(self.entryField.text())
        except ValueError:
            value = 1

        self.display.add_card(value)

    def on_drop(self):
        try:
            value = int(self.entryField.text())
        except ValueError:
            value = 1
        value -= 1  # we're indexing an array

        self.display.drop_card(value)

    def on_invalid(self):
        try:
            value = int(self.entryField.text())
        except ValueError:
            value = 1
        value -= 1

        self.display.x_card(value)

    def on_clear(self):
        self.display.clear_cards()

    def on_reset(self):
        self.display.destroy_self()
        self.display = self.initialize_display()

    @staticmethod
    def on_break():
        print("coffee...")


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # Create and show the form
    mainWindow = MainWindow()
    mainWindow.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
