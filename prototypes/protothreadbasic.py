import time

from PySide2 import QtCore


class TestThread(QtCore.QThread):
    def __init__(self, name):
        QtCore.QThread.__init__(self)
        self.name = name

    def __del__(self):
        self.wait()

    def run(self):
        print(f"start {self.name}")
        time.sleep(2)
        print(f"end {self.name}")


class SendThread(QtCore.QThread):
    def __init__(self, name):
        QtCore.QThread.__init__(self)
        self.name = name
        self.counter = 0

    def __del__(self):
        self.wait()

    def run(self):
        pass


class ReceiveThread(QtCore.QThread):
    def __init__(self, name):
        QtCore.QThread.__init__(self)
        self.name = name

    def __del__(self):
        self.wait()

    def run(self):
        pass


threadA = TestThread("A")
threadB = TestThread("B")
threadR = ReceiveThread("C")
threadS = SendThread("D")

print("done init")

threadA.start()
threadB.start()

time.sleep(3)
