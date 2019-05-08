"""let's test evesdropping on keyboard input"""

import threading
import queue
from functools import partial
import pyWinhook as ph
import pythoncom


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


def keyhandler(keyqueue):
    """track keyboard states and generate events"""
    assert isinstance(keyqueue, queue.Queue)
    ctrl = False

    while True:
        try:
            event = keyqueue.get(block=True, timeout=2)
            # OnKeyboardEvent(event)
            if event.Key == "Lcontrol":
                ctrl = event.Transition == 0
            else:
                if event.Transition == 0 and ctrl:
                    if event.Key == "C":
                        print("Copied")
                    elif event.Key == "X":
                        print("Cut")
                    elif event.Key == "V":
                        print("Pasted")

        except queue.Empty:
            print(".")


def enqueueKey(event, keyqueue):
    assert isinstance(keyqueue, queue.Queue)
    keyqueue.put(event)

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

# initialize hotkey handler:
kh = threading.Thread(target=keyhandler,
                      args=(kq,)
                      )  # daemon=True)
kh.start()

# initialize the listener thread:
li = threading.Thread(target=listener,
                      args=(kq,)
                      )  # daemon=True)
li.start()

print("threads opened successfully")
