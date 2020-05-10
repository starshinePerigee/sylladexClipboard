import sys

from PySide2 import QtCore, QtWidgets

import win32gui as wg


class AnimationIndicator(QtWidgets.QLabel):
    def __init__(self, parent, startpos, endpos):
        super(AnimationIndicator, self).__init__(parent)
        self.setText("<>")
        self.show()
        # noinspection PyTypeChecker
        self.moveAni = QtCore.QPropertyAnimation(self, b"pos")
        self.moveAni.setDuration((endpos-startpos).manhattanLength()*8)
        self.moveAni.setStartValue(startpos)
        self.moveAni.setKeyValueAt(0.5, endpos)
        self.moveAni.setEndValue(startpos)
        self.moveAni.setLoopCount(-1)
        self.moveAni.start()


class MainWindow(QtWidgets.QDialog):
    """The parent window with controls"""
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Sylladex Focus Test")
        self.resize(480, 360)

        self.flag = QtWidgets.QLabel(self)
        self.flag.setText("*")
        self.flag.show()

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        self.text = QtWidgets.QLabel(self)
        self.text.setFrameStyle(QtWidgets.QFrame.Panel |
                                QtWidgets.QFrame.Sunken)
        self.text.setText("<Loading windows...>")
        self.layout.addWidget(self.text)
        self.text.show()

        self.fish = AnimationIndicator(self,
                                       QtCore.QPoint(0, 320),
                                       QtCore.QPoint(440, 320))
        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.list_windows)
        self.timer.start()

    def list_windows(self):
        if self.flag.text() == "~":
            self.flag.setText(" ")
        else:
            self.flag.setText("~")
        self.text.setText(f"Windows: \n"
                          f"Active {wg.GetActiveWindow()}\n"
                          f"Foreground {wg.GetForegroundWindow()}"
                          f" ({wg.GetWindowText(wg.GetForegroundWindow())})\n"
                          f"Focus {wg.GetFocus()}")

if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # Create and show the form
    mainWindow = MainWindow()
    mainWindow.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
