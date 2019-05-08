"""let's test evesdropping on keyboard input"""

import threading
import queue
from functools import partial
import pyWinhook as ph
import pythoncom
from pynput.keyboard import Key, Controller

CTRLS = ("Lcontrol", "Rcontrol")


def OnMouseEvent(event):
    """unused function to pull all info from a mouse event"""
    print('MessageName: %s' % event.MessageName)
    print('Message: %s' % event.Message)
    print('Time: %s' % event.Time)
    print('Window: %s' % event.Window)
    print('WindowName: %s' % event.WindowName)
    print('Position: (%d, %d)' % event.Position)
    print('Wheel: %s' % event.Wheel)
    print('Injected: %s' % event.Injected)
    print('---')

    # return True to pass the event to other handlers
    # return False to stop the event from propagating
    return True


def OnKeyboardEvent(event):
    """unused function to pull all info from a keyboard event"""
    print('MessageName: %s' % event.MessageName)
    print('Message: %s' % event.Message)
    print('Time: %s' % event.Time)
    print('Window: %s' % event.Window)
    print('WindowName: %s' % event.WindowName)
    print('Ascii: %s' % event.Ascii, chr(event.Ascii))
    print('Key: %s' % event.Key)
    print('KeyID: %s' % event.KeyID)
    print('ScanCode: %s' % event.ScanCode)
    print('Extended: %s' % event.Extended)
    print('Injected: %s' % event.Injected)
    print('Alt %s' % event.Alt)
    print('Transition %s' % event.Transition)
    print('---')

    # return True to pass the event to other handlers
    # return False to stop the event from propagating
    return True


def keyhandler(keyqueue, keyboard):
    """track keyboard states and generate events"""
    assert isinstance(keyqueue, queue.Queue)
    ctrl = False
    halt = False

    while not halt:  # noqa R1702
        try:
            event = keyqueue.get(block=True, timeout=2)
            # OnKeyboardEvent(event)
            if event.Key == "Escape":
                halt = True
            elif event.Key in CTRLS:
                ctrl = event.Transition == 0
            else:
                if event.Transition == 0 and ctrl:
                    if event.Key == "C":
                        print("Copied")
                    elif event.Key == "X":
                        print("Cut")
                    elif event.Key == "V":
                        global kctrl  # noqa
                        print("Pasted")
                        # keyboard.press('~')
                        # keyboard.release('~')
                        if kctrl:
                            keyboard.press('v')
                            keyboard.release('v')
                        else:
                            with keyboard.pressed(Key.ctrl):
                                # print("entering paste block, ctrl is " +
                                #       str(keyboard.ctrl_pressed))
                                keyboard.press('v')
                                keyboard.release('v')
                        # print("leaving paste block, ctrl is " +
                        #       str(keyboard.ctrl_pressed))

        except queue.Empty:
            # print(".")
            pass


kctrl = False


def enqueueKey(event, keyqueue):
    """this is our tiny respond to keypress function.

    It should probably be smaller, but we're hacking it apart.
    if this takes too long to return windows will break.
    You should probably sometime make it so it spawns a thread and returns.
    """
    # assert isinstance(keyqueue, queue.Queue)

    if event.Injected != 0:
        return True

    keyqueue.put(event)
    global kctrl  # noqa don't care it's a hack in a prototype module

    if event.Key in CTRLS:
        kctrl = event.Transition == 0
    elif event.Key == "V" and event.Transition == 0 and kctrl:
        # supress paste events
        return False

    return True


def listener(keyqueue):
    """do low level monitoring for keypresses"""
    hm = ph.HookManager()

    # hm.MouseAllButtonsDown = OnMouseEvent
    # hm.KeyAll = OnKeyboardEvent
    f = partial(enqueueKey, keyqueue=keyqueue)
    hm.KeyAll = f

    # hm.HookMouse()
    hm.HookKeyboard()

    pythoncom.PumpMessages()


# initialize key queue:
kq = queue.Queue()

# initialize the keyboard controller:
kb = Controller()

# initialize hotkey handler:
kh = threading.Thread(target=keyhandler,
                      args=(kq, kb,))
kh.start()

# initialize the listener thread:
li = threading.Thread(target=listener,
                      args=(kq,),
                      daemon=True)
li.start()

print("threads opened successfully")
