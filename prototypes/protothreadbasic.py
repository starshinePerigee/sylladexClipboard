import time
import random
import queue

from PySide2 import QtCore


class TestThread(QtCore.QThread):
    def __init__(self, name):
        QtCore.QThread.__init__(self)
        self.name = name

    def __del__(self):
        self.wait()

    def run(self):
        print(f"start {self.name}")
        time.sleep(random.random()*2)
        print(f"end {self.name}")


class SendThread(QtCore.QThread):
    def __init__(self, name, queue):
        QtCore.QThread.__init__(self)
        self.name = name
        self.queue = queue
        print(f"Initializing sender thread {self.name}")

    def __del__(self):
        self.wait()

    def run(self):
        alph = "ABCDEFGHIJKLMNO"
        for i in range(0, 10):
            time.sleep(random.random()*1)
            print(f"Adding {alph[i]} to queue.")
            self.queue.put(alph[i])


class ReceiveThread(QtCore.QThread):
    def __init__(self, name, queue):
        QtCore.QThread.__init__(self)
        self.name = name
        self.queue = queue
        print(f"Initializing receiver thread {self.name}")

    def __del__(self):
        self.wait()

    def run(self):
        count = 0
        while count < 10:
            item = self.queue.get()
            print(f"Processing {item}...")
            time.sleep(random.random()*2)
            count += 1


threadA = TestThread("A")
threadB = TestThread("B")

print("done init")

threadA.start()
threadB.start()

time.sleep(2)

thread_queue = queue.Queue()
threadR = ReceiveThread("C", thread_queue)
threadS = SendThread("D", thread_queue)

threadR.start()
threadS.start()

while not threadR.isFinished():
    time.sleep(1)
