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
# import pywintypes
import win32clipboard as clip
from PIL import ImageGrab, ImageQt
import os

protodir = os.path.dirname(os.path.realpath(__file__))
IMAGE_PATH = os.path.join(protodir, r"card.png")
AREA_PATH = os.path.join(protodir, r"cardarea.png")


class CBFormat:
    # standard format names:
    # https://docs.microsoft.com/en-us/windows/desktop/dataxchg/standard-clipboard-formats
    STANDARD_FORMATS = {
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

    @staticmethod
    def translate_format(cb_format):
        if cb_format in CBFormat.STANDARD_FORMATS:
            # return "standard format " + \
            #        ClipboardRenderer.STANDARD_FORMATS[CBFormat]
            return CBFormat.STANDARD_FORMATS[cb_format][3:]
        return clip.GetClipboardFormatName(cb_format)

    def __init__(self, format_id=None):
        self.id = format_id
        self.name = CBFormat.translate_format(self.id)

    def __str__(self):
        return self.name + f" ({self.id})"


# noinspection PyUnusedLocal
class ClipboardRenderer:
    def __init__(self, area):
        self.bound_rect = area.geometry()
        self.last_pillow = None

    @staticmethod
    def get_all_types():
        data = []
        cb_type = 0
        clip.OpenClipboard()
        while clip.EnumClipboardFormats(cb_type) != 0:
            cb_type = clip.EnumClipboardFormats(cb_type)
            data.append(CBFormat(cb_type))
        clip.CloseClipboard()
        return data

    @staticmethod
    def read_single(cb_format):
        # print("Reading " + translate_format(CBFormat) + " (" + str(CBFormat) + ")")
        if cb_format.id == 3:  # CF_METAFILEPICT NOT SUPPORTED BY win32clipboard
            print("CF_METAFILEPICT not supported by win32clipboard! Returning -1")
            return -1
        try:
            clip.OpenClipboard()
            data = clip.GetClipboardData(cb_format.id)
            clip.CloseClipboard()
            return data
        except TypeError:
            print(f"CLIPBOARD FORMAT UNAVAILABLE: {str(cb_format)}")
            return None

    def draw_area(self):
        disambiguate = {
            1: self.render_text,
            2: self.render_bitmap,
            49446: self.render_html_text,  # HTML Text
            49158: self.render_text  # FileName
        }

        cb_types = self.get_all_types()
        if len(cb_types) == 0:
            return ""

        for cb_type in cb_types:
            if cb_type.id in disambiguate:
                return disambiguate[cb_type.id](cb_type)

        return "<" + str(cb_types[0].name) + ">"

    def disambiguate_draw(self):
        pass

    def render_text(self, cb_format):
        text = str(self.read_single(cb_format))
        text = text.replace("\\n", "<br>").replace("\\r", "")[2:]
        # print(text)
        return text

    def render_html_text(self, cb_format):
        text = str(self.read_single(cb_format))
        start_delimiter = "<html>"
        end_delimiter = "</html>"
        text = text[text.find(start_delimiter):]
        text = text[:text.rfind(end_delimiter)+len(end_delimiter)]
        text = text.replace("\\n", "<br>").replace("\\r", "")
        # print(text)
        return text

    def render_bitmap(self, cb_format):
        self.last_pillow = ImageQt.ImageQt(ImageGrab.grabclipboard())
        # pixmap = QtGui.QPixmap.fromImage(ImageQt.ImageQt(
        #     ImageGrab.grabclipboard()))
        pixmap = QtGui.QPixmap.fromImage(self.last_pillow)
        pixmap_crop = pixmap.copy(self.bound_rect)
        # print(f"h: {pixmap_crop.height()} w: {pixmap_crop.width()}")
        return pixmap_crop


class MainWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Render From Clipboard Test")
        self.resize(480, 240)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        self.entryButton = QtWidgets.QPushButton("Get Clipboard")

        card_pixmap = QtGui.QPixmap(IMAGE_PATH)
        self.card = QtWidgets.QLabel(self)
        self.card.setPixmap(card_pixmap)
        self.card.setGeometry(card_pixmap.rect())
        self.card.move(0, 0)
        self.card.setAlignment(QtCore.Qt.AlignTop)
        self.area = QtWidgets.QLabel(self.card)
        area_pixmap = QtGui.QPixmap(AREA_PATH)
        self.area.setPixmap(area_pixmap)
        self.area.setGeometry(area_pixmap.rect())
        self.area.setMask(area_pixmap.mask())
        # self.area.move(24, 28) - for subset mask
        self.area.move(15, 20)
        self.area.setAlignment(QtCore.Qt.AlignLeft)
        self.area.setAlignment(QtCore.Qt.AlignVCenter)
        # self.area.setWordWrap(True)
        self.typelabel = QtWidgets.QLabel(self.card)
        self.typelabel.setText("<Object Type>")
        self.typelabel.move(18, 166)
        self.typelabel.setStyleSheet("color: #b4fefd")
        self.typelabel.setMaximumWidth(self.card.width()-10)
        self.cb_renderer = ClipboardRenderer(self.area)

        self.text = QtWidgets.QLabel(self)
        self.text.setText("[Clipboard not yet read]")
        # self.text.setWordWrap(True)
        self.text.setAlignment(QtCore.Qt.AlignTop)

        layout.addWidget(self.entryButton, 0, 0, 1, 2)
        layout.addWidget(self.card, 1, 0)
        layout.addWidget(self.text, 1, 1, alignment=QtCore.Qt.AlignTop)
        layout.setColumnStretch(1, 1)

        self.entryButton.clicked.connect(self.read_clipboard)

    def read_clipboard(self):
        text = []
        types = self.cb_renderer.get_all_types()
        for i in types:
            text.append("<b>" + str(i.id) + "</b>: " + str(i.name))

        self.text.setText("<br>".join(text))

        reject_names = (14,  # ENHMETAFILE
                        49161  # DataObject
                        )

        if len(types) > 0:
            if int(types[0].id) in reject_names and len(types) > 1:
                self.typelabel.setText(str(types[1].name)[0:80])
            else:
                self.typelabel.setText(str(types[0].name)[0:80])
        else:
            self.typelabel.setText("NULL")

        image = self.cb_renderer.draw_area()

        if type(image) is str:
            self.area.setText("   " + image)
        elif type(image) is QtGui.QPixmap:
            self.area.setPixmap(image)
        else:
            self.area.setText("<INVALID DATA>")


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # Create and show the form
    mainWindow = MainWindow()
    mainWindow.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
