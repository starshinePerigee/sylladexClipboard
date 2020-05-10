"""This module handles all interfacing with the clipboard.
It provides a single managed thread which card and other modules can
talk to via signals/slots.

signals emitted:
clipboard_updated()
new_card_from_clipboard(Clip)

slots caught:
load_card_to_clipboard(Clip/Card/string)
"""

import sys
import logging
from time import sleep

from PySide2 import QtCore
from PySide2.QtCore import Signal, Slot

import win32clipboard as wc
import pywintypes


class Format:
    """This class represents a single clipboard format. Reference
    https://docs.microsoft.com/en-us/windows/desktop/dataxchg/standard-clipboard-formats
    """

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
    def translate_format(format_id):
        if format_id in Format.STANDARD_FORMATS:
            # return "standard format " + \
            #        ClipboardRenderer.STANDARD_FORMATS[CBFormat]
            return Format.STANDARD_FORMATS[format_id][3:]
        return wc.GetClipboardFormatName(format_id)

    def __init__(self, format_id=None):
        """ Initialize a new Format."""
        if isinstance(format_id, Format):
            self.id = format_id.id
            self.name = format_id.name
        elif format_id:
            # if format_id == 3:  # CF_METAFILEPICT
            #     raise ValueError("CF_METAFILEPICT format not supported "
            #                      "by win32clipboard!")
            self.id = format_id
            self.name = self.translate_format(format_id)
        else:
            self.id = None
            self.name = None

    def __str__(self):
        if self.id:
            return f"{self.name} ({self.id})"
        else:
            return "NULL (0)"

    def __eq__(self, other):
        # return self.id == other.id and self.name == other.name
        if isinstance(other, int):
            return self.id == other
        return self.id == other.id

    def __ne__(self, other):
        return not self == other


class Datum:
    """Contains a single clipboard data-format pair"""
    def __init__(self, data=None, format_=None):
        self.data_types = None
        if data is None:
            self.data = None
            self.format = Format(None)
        elif isinstance(data, Datum):
            self.data = data.data
            self.format = data.format
        else:
            self.data, serial_format = self.serialize(data)
            if format_:
                self.format = Format(format_)
            else:
                self.format = Format(serial_format)

    def serialize(self, data):
        if self.data_types is None:
            self.data_types = {
                "QImage": self._load_qimage
            }
        if data is not None:
            data_type = type(data).__name__
            return self.data_types.get(data_type, self._load_arbitrary)(data)

    @staticmethod
    def _load_arbitrary(data):
        return data, 13

    @staticmethod
    def _load_qimage(data):
        # TODO: support multiple image formats
        ba = QtCore.QByteArray()
        buffer = QtCore.QBuffer(ba)
        buffer.open(QtCore.QIODevice.WriteOnly)
        data.save(buffer, "PNG")
        return buffer.data(), 49927

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
        if isinstance(other, Datum):
            return self.data == other.data and self.format == other.format
        else:
            return False

    def __ne__(self, other):
        return not self == other


class Clip:
    """
    This class contains the contents of one (1) clipboard. It is empty on
    init, so typically you'll get it as a return value from Handler functions.
    """
    running_id = -1

    def __init__(self, data=None, seq_num=None):
        """
        Create a new clip with data; pass none for an empty clip
        """
        if seq_num:
            self.seq_num = seq_num
        elif isinstance(data, Clip):
            self.seq_num = data.seq_num
        else:
            self.seq_num = Clip.running_id
            Clip.running_id -= 1
        self.data = []
        self.data_containers = None
        self.add_data(data)

    def add_data(self, data, list_recursion=False):
        """ append an arbitrary data object to the end of this clip's data.

        When run on a list, it appends the list as multiple objects and will
        recurse into itself on individual items. However, it only does this;
        [[1, 2]] will load a single datum with data [1, 2]
        """
        if self.data_containers is None:
            self.data_containers = {
                "Datum": self._add_datum,
                "Clip": self._add_clip,
                "list": self._add_list,
            }
        if data is not None:
            data_type = type(data).__name__
            if data_type == "list" and list_recursion:
                self._add_arg(data)
            else:
                self.data_containers.get(data_type, self._add_arg)(data)

    def _add_datum(self, data):
        self.data += [data]

    def _add_list(self, data):
        for i in data:
            self.add_data(i, list_recursion=True)

    def _add_clip(self, data):
        self.data += data.data

    def _add_arg(self, data):
        self.data += [Datum(data)]

    def formats(self):
        return [x.format for x in self.data]

    def find(self, format_order):
        if format_order is None:
            return Datum()
        if isinstance(format_order, int) or isinstance(format_order, Format):
            format_order = [format_order]
        clip_formats = self.formats()
        for format_ in format_order:
            # note that Format.__eq__ accepts ints;
            # this means you can do "13 in <list of Format>
            if format_ in clip_formats:
                return self.data[clip_formats.index(format_)]
        raise LookupError(f"No priority formats in format_order present in clip data!")

    def print_all(self):
        print(f"***Clip ID {self.seq_num} with {len(self)} elements:")
        for i in self.data:
            print("   " + str(i))

    def __str__(self):
        return f"Clip {self.seq_num}; {len(self)} element(s), first element " \
               f"{str(self[0])}"

    def __add__(self, other):
        clip = Clip(self)
        clip.add_data(other)
        return clip

    def __radd__(self, other):
        return Clip(other) + self

    def __eq__(self, other):
        return self.seq_num == other.seq_num and self.data == other.data

    def __len__(self):
        return len(self.data)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            self.data[key] = [Datum(i) for i in value]
        else:
            self.data[key] = Datum(value)

    def __getitem__(self, key):
        if len(self) == 0 and key == 0:
            return Datum()
        return self.data[key]

    def __delitem__(self, key):
        del self.data[key]


# module global for a global resource
cb_mutex = QtCore.QMutex()


class Handler:
    """ Handler provides a contextmanager-type interface to win32clipboard
    which uses cliphandler data types and has useful utility functions.

    Most references to win32clipboard should be in this class to make changing
    libraries easier (if necessary), like if we ever want cross-platform support.
    """
    # ref http://timgolden.me.uk/pywin32-docs/win32clipboard.html
    # https://docs.microsoft.com/en-us/windows/win32/dataxchg/clipboard-operations
    def __init__(self):
        logging.info("Initializing clipboard.")
        self.current_seq = 0
        self.seq()

    def write(self, data):
        """Write a piece of data to the clipboard, overwriting the current
        contents."""
        wc.EmptyClipboard()
        if not isinstance(data, Clip):
            data = Clip(data)
        success = False
        for item in data:
            if item.data is None:
                logging.info(f"Skipping None: {item}")
                continue
            try:
                wc.SetClipboardData(item.format.id, item.data)
                success = True
            except pywintypes.error:
                error = sys.exc_info()
                if error[1].strerror == "The handle is invalid.":
                    logging.warning(f"The handle for {item} is invalid and will be skipped.")
        if not success:
            logging.error(f"Could not write {data} as all data were invalid.")
        self.seq()

    def read(self):
        """ Read the current contents of the clipboard and return it as a Clip"""
        clip = Clip(seq_num=self.seq())
        for format_ in self._get_all_formats():
            clip.add_data(self._read_single(format_))
        return clip

    @staticmethod
    def _get_all_formats():
        """ Read all data formats currently on the clipboard.
        Returns as a list of ints"""
        all_formats = []
        current_format = 0
        while wc.EnumClipboardFormats(current_format) != 0:
            current_format = wc.EnumClipboardFormats(current_format)
            all_formats.append(current_format)
        return all_formats

    @staticmethod
    def _read_single(format_):
        if isinstance(format_, Format):
            format_ = format_.id
        if format_ == 3:  # CF_METAFILEPICT NOT SUPPORTED BY win32clipboard
            logging.warning("CF_METAFILEPICT not supported by win32clipboard! Returning None")
            return Datum()
        try:
            data = wc.GetClipboardData(format_)
            return Datum(data, format_)
        except TypeError:
            logging.warning(f"CLIPBOARD FORMAT UNAVAILABLE: "
                            f"{Format.translate_format(format_)}")
            return Datum()

    def clear(self):
        """Empties the contents of the current clipboard."""
        wc.EmptyClipboard()
        self.seq()

    def seq(self):
        """Reads the current clipboard sequence number and updates the internal
        seq variable."""
        self.current_seq = wc.GetClipboardSequenceNumber()
        return self.current_seq

    def __enter__(self):
        try_count = 0
        while try_count < 100:
            if cb_mutex.tryLock(10):
                try:
                    wc.OpenClipboard()
                    return self
                except pywintypes.error as e:
                    # do some wrangling to try to get the clipboard open
                    if e.strerror == "Access is denied.":
                        logging.warn(f"Clipboard access is denied.")
                        # try:
                        #     wc.CloseClipboard()
                        #     sleep(0.005)
                        # except pywintypes.error as e2:
                        #     if e2.strerror != "Thread does not have a clipboard open":
                        #         raise e2
                        cb_mutex.unlock()
                    else:
                        raise e
            else:
                try_count += 1
        raise RuntimeError("Cannot get clipboard mutex lock!")

    def __exit__(self, exception_type=None, exception_value=None, traceback=None):
        # ref http://effbot.org/zone/python-with-statement.htm
        if exception_type:
            print(f"Exception found! {exception_type} {exception_value} {traceback}")

        try:
            wc.CloseClipboard()
            sleep(0.005)
            cb_mutex.unlock()
        except pywintypes.error as e:
            if e.strerror == "Thread does not have a clipboard open.":
                logging.warning("Could not close clipboard, "
                                "thread does not have a clipboard open.")
            else:
                raise e


class Monitor(QtCore.QObject):
    """The top level clipboard handler class. Runs as its own thread, accepts
    events in and out to read/write/set.
    TODO: (bind to Clip objects when they're created??)
    """
    clipboard_updated = Signal()
    new_card_from_clipboard = Signal(Clip)

    def __init__(self):
        super().__init__()
        # if thread is None:
        #     thread = QtCore.QThread()
        # self.thread = thread
        self.handler = Handler()
        self.timer = None
        self.try_count = 0

    @Slot()
    def check_clipboard(self):
        if self.check_seq():
            self.clipboard_updated.emit()
            try:
                with self.handler:
                    new_clip = self.handler.read()
                self.new_card_from_clipboard.emit(new_clip)
            except RuntimeError as e:
                if str(e) == "Cannot get clipboard mutex lock!":
                    self._reset_clipboard_lock()
                    # should attempt again because handler.seq hasn't been
                    # updated since read would have failed.

    def check_seq(self):
        if cb_mutex.tryLock(10):
            self.try_count = 0
            new_seq = wc.GetClipboardSequenceNumber()
            sleep(0.005)
            cb_mutex.unlock()
            return new_seq != self.handler.current_seq
        if self.try_count < 500:
            self.try_count += 1
            # self.thread.yieldCurrentThread()
        else:
            self._reset_clipboard_lock()
            self.try_count = 0
        return False

    def _reset_clipboard_lock(self):
        # DANGEROUS MAYBE
        logging.error("Clipboard mutex hung and must be force reset")
        try:
            wc.CloseClipboard()
        except pywintypes.error:
            pass
        cb_mutex.unlock()

    @Slot()
    def load(self, clip):
        with self.handler:
            self.handler.write(clip)

    @Slot()
    def begin(self):
        # self.thread.start()
        # self.moveToThread(self.thread)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(0)
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start()

    @Slot()
    def end(self):
        self.timer.stop()
        # self.thread.quit()
        # self.thread.wait()


if __name__ == '__main__':
    clipboard_thread = Monitor()
    clipboard_thread.start()
