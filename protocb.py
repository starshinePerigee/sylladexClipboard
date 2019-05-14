"""lets just test clipboard junk

this monitors the clipboard, prints info when something comes in,
and keeps a four-wide FIFO queue

copy "q" as notepad plaintext to halt the program.

https://docs.activestate.com/activepython/3.2/pywin32/win32clipboard.html
https://docs.microsoft.com/en-us/windows/desktop/dataxchg/about-the-clipboard
"""

import sys
from time import sleep
import ipdb
import pywintypes
import win32clipboard as clip

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


def explodeType(target):
    try:
        types = []
        for i in target:
            types.append(type(i))
        return (str(len(target)) + "-element " + str(type(target)) +
                ": " + str(types))
    except TypeError:
        return str(type(target))


def shortPrint(item, length=80):
    cstring = str(item)
    if len(cstring) > length:
        cstring = cstring[:length]
    return cstring


def formatName(format):
    if format in STANDARDFORMATS:
        return "standard format " + STANDARDFORMATS[format]
    # print("looking up " + str(format))
    return clip.GetClipboardFormatName(format)


def cbwrite(data, formats):
    clip.EmptyClipboard()
    if data is not None:
        for i in range(0, len(data)):
            # if formats[i][0] == 3:
            #     #print("CF_METAFILEPICT not supported by win32clipboard!")
            #     pass
            # else:
            print("writing \"" + shortPrint(data[i]) + "\" as " +
                  str(formats[i][1]))
            try:
                clip.SetClipboardData(formats[i][0], data[i])
            except pywintypes.error:
                error4 = sys.exc_info()
                if error4[1].strerror == 'The handle is invalid.':
                    print("The handle for datatype '" + formats[i][1] +
                          "' is invalid. Skipping...")


def cbSingleRead(format):
    # print("Reading " + formatName(format) + " (" + str(format) + ")")
    if format == 3:  # CF_METAFILEPICT NOT SUPPORTED BY win32clipboard
        print("CF_METAFILEPICT not supported by win32clipboard! Returning -1")
        return -1
    try:
        return clip.GetClipboardData(format)
    except TypeError:
        print("CLIPBOARD FORMAT UNAVAILABLE: " + formatName(format) +
              " (" + str(format) + ")")
        return None


def cbread(format):
    if format is None:
        return None

    if isinstance(format, int):
        return cbSingleRead(format)

    if len(format) == 0:
        return None

    data = []
    for f in format:
        data.append(cbSingleRead(f[0]))
    return data


def cbtypes():
    data = []
    type = 0
    while clip.EnumClipboardFormats(type) != 0:
        type = clip.EnumClipboardFormats(type)
        data.append((type, formatName(type)))
    return data


halt = False
seqNumber = None
cbQueue = [(None, None), (None, None), (None, None)]
while not halt:
    try:
        if clip.GetClipboardSequenceNumber() != seqNumber:
            print("\r\n*****************\r\n")
            clip.OpenClipboard()
            print("seq#: " + str(clip.GetClipboardSequenceNumber()))
            cTypes = cbtypes()
            print("types: " + str(cTypes))
            # print("type^2: " + explodeType(cTypes))
            cData = cbread(cTypes)
            print("data: " + shortPrint(cData))
            print("data type: " + explodeType(cData))

            # ipdb.set_trace()
            print("\r\n")
            try:
                if cData[0] == 'q':
                    clip.EmptyClipboard()
                    halt = True
                elif cData[0] == 'd':
                    ipdb.set_trace()
                    clip.EmptyClipboard()
                    clip.CloseClipboard()
            except TypeError:
                pass

            cbwrite(cbQueue[0][0], cbQueue[0][1])

            nSeqNumber = clip.GetClipboardSequenceNumber()
            print("new seq#: " + str(nSeqNumber))
            nTypes = cbtypes()
            print("new type: " + str(nTypes))
            # print("new type^2: " + explodeType(nTypes))
            nData = cbread(nTypes)
            print("new data: " + shortPrint(nData))
            print("new data type: " + explodeType(nData))
            clip.CloseClipboard()
            seqNumber = clip.GetClipboardSequenceNumber()
            print("newest seq #: " + str(seqNumber))
            cbQueue.append((cData, cTypes))
            cbQueue.pop(0)

            print("\r\nqueue: [" + shortPrint(cbQueue[0][0], 8) +
                  "][" + shortPrint(cbQueue[1][0], 8) +
                  "][" + shortPrint(cbQueue[2][0], 8) + "]")
            seqNumber = nSeqNumber

            # ipdb.set_trace()
    except pywintypes.error:
        error1 = sys.exc_info()
        if error1[1].strerror == 'Access is denied.':
            print("Access denied")
            try:
                owner = clip.GetClipboardOwner()
                print("Clipboard is owned by " + str(owner))
            except pywintypes.error:
                error2 = sys.exc_info()
                if (error2[1].funcname == 'GetClipboardOwner' and
                        error2[1].strerror == "Access is denined."):
                    print("Can't read owner")
                else:
                    print("ERROR DURING OWNER CHECK: \r\n" + str(error2))
        else:
            print(error1)
            print("ERROR DURING CLIPBOARD OPERATION: \r\n" + str(error1))
            # ipdb.set_trace()
    sleep(0.1)
