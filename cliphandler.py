"""This module handles all interfacing with the clipboard.
It provides a single managed thread which card and other modules can
talk to via signals/slots.

signals emitted:
clipboard_updated()
new_card_from_clipboard(Clip)

slots caught:
load_card_to_clipboard(Clip/Card/string)
"""

from PySide2 import QtCore
from PySide2.QtCore import Signal, Slot

import win32clipboard as wc
import pywintypes


class Format:
    """This class represents a single instance of a clipboard format, as
    """
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

    python_formats = {
        "str": 13
    }

    @staticmethod
    def translate_format(cb_format):
        """Convert a format specifier number into a human-readable format name."""
        if cb_format in Format.STANDARD_FORMATS:
            # return "standard format " + \
            #        ClipboardRenderer.STANDARD_FORMATS[CBFormat]
            return Format.STANDARD_FORMATS[cb_format][3:]
        return wc.GetClipboardFormatName(cb_format)

    @staticmethod
    def from_data(data=None):
        if data is None:
            return Format()
        data_type = type(data).__name__
        if data_type in Format.python_formats:
            new_id = Format.python_formats[data_type]
        else:
            new_id = 12
        return Format(new_id)

    def __init__(self, format_id=None):
        if format_id:
            self.id = format_id
            self.name = Format.translate_format(self.id)
        else:
            self.id = None
            self.name = None

    def __str__(self):
        return f"{self.name} ({self.id})"


class Single:
    """Contains a single clipboard data-format pair"""
    def __init__(self, data=None, format=None):
        self.data = data
        if format is None:
            self.format = Format.from_data(data)
        else:
            self.format = format
        if format == 3:  # CF_METAFILEPICT
            raise ValueError("CF_METAFILEPICT format not supported "
                             "by win32clipboard!")

    def string_preview(self, length=80):
        preview = str(self.data)
        if len(preview) > length:
            preview = preview[:length]
        return preview

    def __str__(self):
        return f"<{self.format} '{self.string_preview(40)}'>"

    def __add__(self, other):
        return Clip(self) + other

    def __radd__(self, other):
        return Clip(other) + self

    def __eq__(self, other):
        if isinstance(other, Single):
            return self.data == other.data and self.format == other.format
        else:
            return False


class Clip:
    """
    This class contains the contents of one (1) clipboard. It is empty on
    init, so typically you'll get it as a return value from Handler functions.
    """
    running_id = -1

    def __init__(self, data=None):
        """
        Create a new empty clip
        """
        if isinstance(data, Clip):
            self.seq_num = data.seq_num
        else:
            self.seq_num = Clip.running_id
            Clip.running_id -= 1
        self.data = []
        self.add_data(data)

    def add_data(self, data):
        overload = {
            "Single": self._add_single,
            "Clip": self._add_clip,
            "list": self._add_list
        }
        if data is not None:
            data_type = type(data).__name__
            if data_type in overload:
                overload[data_type](data)
            else:
                raise TypeError(f"Invalid type! Received {type(data)},"
                                f"expected single, clip, list, or none.")

    def _add_single(self, data):
        self.data += [data]

    def _add_list(self, data):
        if isinstance(data[0], Single):
            self.data += data
        else:
            raise TypeError(f"Invalid type present in list! Received "
                            f"{type(data[0])}, expected list of Singles")

    def _add_clip(self, data):
        self.data += data.data

    def formats(self):
        return [x.format for x in self.data]

    def __str__(self):
        return f"Clip {self.seq_num}"

    def __add__(self, other):
        return Clip(self).add_data(other)

    def __radd__(self, other):
        return Clip(other) + self


class Handler:
    def __init__(self):
        print("Initializing clipboard...")

    def write_clipboard(self, data):
        """Write a piece of data to the clipboard, overwriting the current
        contents."""
        wc.EmptyClipboard()
        if isinstance(data, Clip):
            pass
        else:
            pass

    def read_clipboard(self):
        clip = Clip()
        return clip


class Monitor(QtCore.QThread):
    """The top level clipboard handler class. Runs as its own thread.
    """

    def __init__(self):
        super(Monitor, self).__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        halt = False
        seq_num = None
        while not halt:
            if wc.GetClipboardSequenceNumber() != seq_num:
                pass


if __name__ == '__main__':
    clipboard_thread = Monitor()
    clipboard_thread.start()