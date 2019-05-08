"""let's test evesdropping on keyboard input"""

import threading
import queue
from functools import partial
import pynput.keyboard as pk

CTRLS = (pk.Key.ctrl, pk.Key.ctrl_l, pk.Key.ctrl_r)


def keyhandler(keyqueue):
    """track keyboard states and generate events"""
    assert isinstance(keyqueue, queue.Queue)
    ctrl = False
    global kctrl  # noqa

    exit = False
    while not exit:
        try:
            key = keyqueue.get(block=True, timeout=2)
            # print(str(key) + " c:" + str(ctrl) + " k:" + str(kctrl))
            if key[0] in CTRLS:
                if not key[1]:
                    ctrl = False
                else:
                    ctrl = True

            # print("key type: " + str(type(key[0])))
            if ctrl and key[1] and isinstance(key[0], pk._win32.KeyCode):
                if key[0].char == 'c':
                    print("Copied")
                elif key[0].char == "x":
                    print("Cut")
                elif key[0].char == "v":
                    print("Pasted")

            if key[0] == pk.Key.esc:
                exit = True

        except queue.Empty:
            print(".")
            if ctrl or kctrl:
                print("c:" + str(ctrl) + " k:" + str(kctrl))
                raise Exception("CTRL should not be set right now!")


kctrl = False


def enqueueKey(key, keyqueue):
    """this is our tiny respond to keypress function.

    It should probably be smaller, but we're hacking it apart"""
    keyqueue.put((key, True))

    global kctrl  # noqa don't care it's a hack in a prototype module
    if key in CTRLS:
        kctrl = True

    global listener  # noqa see above
    if isinstance(key, pk._win32.KeyCode):
        if key.char == "v":  # and kctrl:
            listener.suppress_event()


def releaseMod(key, keyqueue):
    """this just updates the modifier key counts"""
    keyqueue.put((key, False))

    global kctrl  # noqa see above
    if key in CTRLS:
        kctrl = False


# initialize key queue:
kq = queue.Queue()

# initialize hotkey handler:
kh = threading.Thread(target=keyhandler,
                      args=(kq,))  # daemon=True)
kh.start()

# initialize the listener:
listener = pk.Listener(
    on_press=partial(enqueueKey, keyqueue=kq),
    on_release=partial(releaseMod, keyqueue=kq))
listener.start()

print("threads opened successfully")
