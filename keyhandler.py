"""
This module provides an interface to pywinhook for keyboard IO handling.
We use pywinhook for two reasons:
- we can intercept keys and prevent them from reaching applications
    (ie: blocking copy/paste commands, implimenting hotkeys)
- this lets us get keyboard input without focus.
"""