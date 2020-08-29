"""
This module provides an interface to pywinhook for keyboard IO handling.
We use pywinhook for two reasons:
- we can intercept keys and prevent them from reaching applications
    (ie: blocking copy/paste commands, implementing hotkeys)
- this lets us get keyboard input without focus.

signals emitted:
new_key_combo(Keyset)
listening_key(Keyset)


slots caught:
register_key_combo(Keyset)
begin_listening(Keyset)
"""
# https://sourceforge.net/p/pyhook/wiki/PyHook_Tutorial/

from PySide2 import QtCore
from PySide2.QtCore import Signal, Slot

import pyWinhook as ph
import pythoncom
from pynput.keyboard import Key, Controller

