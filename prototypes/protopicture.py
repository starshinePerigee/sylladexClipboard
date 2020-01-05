"""this is a quick prototype used to generate pictures based on clipboard
data. This also tests UI threading!

https://wxpython.org/Phoenix/docs/html/dataobject_overview.html#dataobject-overview
https://docs.microsoft.com/en-us/windows/desktop/dataxchg/standard-clipboard-formats

https://nikolak.com/pyqt-threading-tutorial/
https://stackoverflow.com/questions/37252756/simplest-way-for-pyqt-threading/37256736
https://stackoverflow.com/questions/1595649/threading-in-a-pyqt-application-use-qt-threads-or-python-threads/1645666
"""
import sys
from PySide2 import QtCore, QtWidgets, QtGui
import pywintypes
import win32clipboard as clip

IMAGE_PATH = r"C:\Users\McGiffenK\Desktop\testpy\sylladex\prototypes\card.png"

# standard format names:
# https://docs.microsoft.com/en-us/windows/desktop/dataxchg/standard-clipboard-formats
STANDARDFORMATS = {
    2: "CF_BITMAP",
    8: "CF_DIB",
    17: "CF_DIBV5",
    5: "CF_DIF",
    0x0082: "CF_DSPBITMAP",
    0x008E: "CF_DSPENHMETAFILE",
    0x0083: "CF_DSPMETAFILEPICT",
    0x0081: "CF_DSPTEXT",
    14: "CF_ENHMETAFILE",
    0x0300: "CF_GDIOBJFIRST",
    0x03FF: "CF_GDIOBJLAST",
    15: "CF_HDROP",
    16: "CF_LOCALE",
    3: "CF_METAFILEPICT",
    7: "CF_OEMTEXT",
    0x0080: "CF_OWNERDISPLAY",
    9: "CF_PALETTE",
    10: "CF_PENDATA",
    0x0200: "CF_PRIVATEFIRST",
    0x02FF: "CF_PRIVATELAST",
    11: "CF_RIFF",
    4: "CF_SYLK",
    1: "CF_TEXT",
    6: "CF_TIFF",
    13: "CF_UNICODETEXT",
    12: "CF_WAVE"
}


class ClipboardRenderer():
    def __init__(self):
        pass


class MainWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Render From Clipboard Test")
        self.resize(320, 240)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        self.cb_renderer = ClipboardRenderer()

        self.entryButton = QtWidgets.QPushButton("Get Clipboard")

        self.card = QtWidgets.QLabel(self)
        self.card.setPixmap(QtGui.QPixmap(IMAGE_PATH))

        self.text = QtWidgets.QLabel(self)
        self.text.setText("[Clipboard not yet read]")

        layout.addWidget(self.entryButton, 0, 0, 1, 2)
        layout.addWidget(self.card, 1, 0)
        layout.addWidget(self.text, 1, 1, alignment=QtCore.Qt.AlignTop)

        self.entryButton.clicked.connect(self.read_clipboard)

    def read_clipboard(self):
        # self.text.setText(self.cb_renderer.get_single_type(0))
        pass


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # Create and show the form
    mainWindow = MainWindow()
    mainWindow.show()
    # Run the main Qt loop
    sys.exit(app.exec_())