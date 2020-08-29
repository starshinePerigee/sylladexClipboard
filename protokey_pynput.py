"""Lets test evesdropping on keyboard input!
(only using a library we're already importing and which is much better
supported!!

This test function:
- evesdrops on keyboard input and prints it to console
- begins listening to keypress sequences when alt-insert is pressed
- saves them as a hotkey for a different keypress
- deletes keypress sequences when alt-delete is pressed
- quits and unbinds all keys when alt-q is pressed
"""

import threading
import queue

import pynput


def listener(keyqueue):
    dir(keyqueue.get(block=True))


def monitor(keyqueue):
    pass


keyqueue = queue.Queue()

monitor_thread = threading.Thread(target=monitor,
                                  args=(keyqueue,))
monitor_thread.start()

listener_thread = threading.Thread(target=listener,
                                   args=(keyqueue,),
                                   daemon=True)
listener_thread.start()

print("threads opened successfully")