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


class SharedClass:
    def __init__(self):
        self.fast_var = 0
        self.slow_var = 0

    def read(self, string):
        print(f"{string}:  fast: {self.fast_var};  slow: {self.slow_var}")

    def write(self, string):
        self.read(string + " before")
        self.fast_var += 1
        time.sleep(2)
        self.slow_var += 1
        self.read(string + " after ")

class SharedThread(QtCore.QThread):
    wait = 0
    def __init__(self, name, shareable):
        QtCore.QThread.__init__(self)
        self.name = name
        self.ID = f"Thread {self.name}"
        self.wait = SharedThread.wait
        SharedThread.wait += 0.5
        self.count = 0
        self.shareable = shareable

    def __del__(self):
        self.wait()

    def run(self):
        string = self.ID + str(self.count)
        self.shareable.read(string + " init  ")
        for i in range (0, 3):
            time.sleep(self.wait)
            self.shareable.write(string)
            self.count += 1
            string = self.ID + str(self.count)
        self.shareable.read(string + " final ")



threadA = TestThread("A")
threadB = TestThread("B")

print("done init")

threadA.start()
threadB.start()

while threadA.isRunning() or threadB.isRunning():
    time.sleep(1)

print("~ ~ ~ ~ ~ ")

share = SharedClass()
threadC = SharedThread("C", share)
threadD = SharedThread("D", share)
threadE = SharedThread("E", share)

threadC.start()
threadD.start()
threadE.start()

while threadC.isRunning() or threadE.isRunning():
    time.sleep(1)

share.read("final final")

print("~ ~ ~ ~ ~ ")

thread_queue = queue.Queue()
threadR = ReceiveThread("F", thread_queue)
threadS = SendThread("G", thread_queue)

threadR.start()
threadS.start()

while not threadR.isFinished():
    time.sleep(1)
