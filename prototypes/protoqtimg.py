import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QWidget, QLabel
from PySide2.QtGui import QIcon, QPixmap


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 image'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.setWindowFlags(self.windowFlags() |
                            Qt.Tool |
                            Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create widget
        pixmap = QPixmap('card.png')
        label = QLabel(self)
        label.setPixmap(pixmap)

        label2 = QLabel(self)
        label2.setPixmap(pixmap)
        label2.move(100, 100)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())