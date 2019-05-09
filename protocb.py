"""lets just test clipboard junk

this monitors the clipboard, prints info when something comes in,
and replaces it with a plaintext version of the copied item.

copy "quit" as notepad plaintext to halt the program.

https://docs.activestate.com/activepython/3.2/pywin32/win32clipboard.html
https://docs.microsoft.com/en-us/windows/desktop/dataxchg/about-the-clipboard
"""

from time import sleep
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


def cbwrite(text):
    clip.EmptyClipboard()
    clip.SetClipboardText(text)


def cbread(format):
    data = clip.GetClipboardData(format)
    return data


def cbtypes():
    data = []
    i = 0
    while clip.EnumClipboardFormats(i) != 0:
        format = clip.EnumClipboardFormats(i)
        # print(format)
        if format in STANDARDFORMATS:
            flist = (format, STANDARDFORMATS[format])
        else:
            flist = (format, clip.GetClipboardFormatName(format))
        data.append(flist)
        i += 1
    return data


halt = False
buffer = None
while not halt:

    try:
        clip.OpenClipboard()
        types = cbtypes()
        current = cbread(types[0][0])
        clip.CloseClipboard()
        if current != buffer:
            print(types)
            buffer = current
            cstring = str(current)
            if len(cstring) > 200:
                cstring = cstring[:200] + "\r\n..."
            print(cstring)
            if cstring == "q":
                halt = True
            print("\r\n")
    except:
        print("Access denied")
        try:
            owner = clip.GetClipboardOwner()
            print("Clipboard is owned by " + str(owner))
        except:
            print("Can't read owner")

    sleep(0.05)
