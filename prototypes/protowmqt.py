import sys
from PySide2.QtCore import Qt, Signal, QPoint, QPropertyAnimation
from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, \
    QVBoxLayout, QWidget, QLabel, QGraphicsOpacityEffect
from PySide2.QtGui import QPixmap

# default image for new cards:
IMAGE_PATH = r"C:\Users\McGiffenK\Desktop\testpy\sylladex\prototypes\card.png"
PUNCHED_PATH = r"C:\Users\McGiffenK\Desktop\testpy\sylladex\prototypes\punched.png"
# offset to use when fading in new cards:
OFFSET = QPoint(50, 50)
OFFSET_DELAY = 0.05
# time duration to fade in a card:
FADE_IN_DURATION = 0.5
FADE_IN_POSITION = QPoint(-30, -30)
# card destruction offset:
DESTROY_OFFSET = [0, -100]
# spacing between cards:
CARD_SPACE = 50
# xy location of the first card:
START_POINT = QPoint(100, 100)


class SylladexCard(QLabel):
    clicked = Signal(str)
    # there is currently an issue where label clickable bounding boxes are
    # rectangles only - this would need to inherit from QGraphicsObject
    # ref https://stackoverflow.com/questions/29372383/qt-mousepressevent-modify-the-clickable-area
    runningID = 0

    def __init__(self, parent=None, startpoint=QPoint(0, 0), delay=0.0):
        self.ID = SylladexCard.runningID
        SylladexCard.runningID += 1

        super(SylladexCard, self).__init__(parent)
        self.clicked.connect(self.mousePressEvent)

        self.unpunched = QPixmap(IMAGE_PATH)
        self.punched = QPixmap(PUNCHED_PATH)
        self.isPunched = False
        self.setPixmap(self.unpunched)

        self.position = startpoint+FADE_IN_POSITION
        self.move(self.position)
        self.moveani = QPropertyAnimation(self, b"pos")

        self.alpha = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.alpha)
        self.alpha.setOpacity(0)
        self.alphaValue = 0
        self.fadeani = QPropertyAnimation(self.alpha, b"opacity")

        self.IDLabel = QLabel(str(self.ID), self)
        self.IDLabel.move(15, 18)
        self.IDLabel.show()

        self.fade_animation(1, FADE_IN_DURATION, delay)
        self.move_animation(startpoint, FADE_IN_DURATION, delay)

        self.show()

    @staticmethod
    def arbitrary_animation(animation, oldvalue, newvalue,
                            duration, delay=0.0):
        # http://zetcode.com/pyqt/qpropertyanimation/
        animation.setDuration((duration + delay) * 1000)
        animation.setStartValue(oldvalue)
        animation.setKeyValueAt(delay/(delay+duration), oldvalue)
        animation.setEndValue(newvalue)
        animation.start()

    def fade_animation(self, newalpha, duration, delay=0.0):
        self.arbitrary_animation(self.fadeani, self.alphaValue, newalpha,
                                 duration, delay)
        self.alphaValue = newalpha

    def move_animation(self, newpos, duration, delay=0.0):
        self.arbitrary_animation(self.moveani, self.position, newpos,
                                 duration, delay)
        self.position = newpos

    def tick(self):
        pass

    def mousePressEvent(self, event):
        if self.isPunched:
            self.setPixmap(self.unpunched)
        else:
            self.setPixmap(self.punched)
        self.isPunched = not self.isPunched


class CardDisplay(QWidget):

    def __init__(self, parent=None):
        super(CardDisplay, self).__init__(parent)
        self.setWindowTitle("Sylladex Card Display")
        #set size to fill the screen
        self.setGeometry(self.screen().availableGeometry())

        self.setWindowFlags(self.windowFlags() |
                            Qt.Tool |
                            Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.cards = []

        self.show()

    def screenModulo(self, point):
        ds = self.screen().availableGeometry()
        return(QPoint(point.x() % ds.width() + ds.x(),
                      point.y() % ds.height() + ds.y()))

    def add_card(self, count):
        for i in range(0, count):
            self.cards.append(SylladexCard(self, self.screenModulo(
                    OFFSET*len(self.cards)+START_POINT), i * OFFSET_DELAY))
            print(f"Card added - there are now {len(self.cards)} cards in the display.")


class MainWindow(QDialog):
    """The parent window with controls"""
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Sylladex Display Manager Test")

        # create widgets and add to layout:
        layout = QVBoxLayout()
        self.entryField = QLineEdit("")
        layout.addWidget(self.entryField)
        self.textButton = QPushButton("Read Text")
        layout.addWidget(self.textButton)
        self.addCardButton = QPushButton("Add Card")
        layout.addWidget(self.addCardButton)
        self.dropCardButton = QPushButton("Drop Card")
        layout.addWidget(self.dropCardButton)
        self.invalidCardButton = QPushButton("Invalid Card")
        layout.addWidget(self.invalidCardButton)
        self.clearAllButton = QPushButton("Clear All")
        layout.addWidget(self.clearAllButton)
        self.resetSylButton = QPushButton("Reset Sylladex")
        layout.addWidget(self.resetSylButton)
        self.breakButton = QPushButton("Break")
        layout.addWidget(self.breakButton)

        # Set dialog layout
        self.setLayout(layout)

        # initialize display window
        self.display = self.initialize_display()

        # bind buttons
        self.textButton.clicked.connect(self.on_press)
        self.breakButton.clicked.connect(self.on_break)
        self.addCardButton.clicked.connect(self.on_add)

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

    def on_break(self):
        print("coffee...")


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    mainWindow = MainWindow()
    mainWindow.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
