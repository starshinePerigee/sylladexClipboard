"""
This prototypes threading using qthreads, as well as passing data between
threads and dealing with long operation times (such as for clipboard rendering)
"""
import sys
from PySide2 import QtCore, QtWidgets

# goal: manage 5 inputs and 3 outputs, but each input pipes to all four outputs
# inputs: pyhook, clipboard, timer, UI button, and second UI window gaining focus
# outputs: print, qlabel text timestamped log, constantly animating widget,
# child window (also has an animated back and forth widget), status display


class ThreadMonitor():
    def __init__(self, parent, name, row):
        self.name = name
        self.status = "uninitialized"
        self.thread_id = "---"
        self.name_label = QtWidgets.QLabel(parent)
        self.name_label.setText(self.name)
        self.status_label = QtWidgets.QLabel(parent)
        self.status_label.setText(self.status)
        self.id_label = QtWidgets.QLabel(parent)
        self.id_label.setText(self.thread_id)
        parent.layout.addWidget(self.name_label, row, 0)
        parent.layout.addWidget(self.status_label, row, 2)
        parent.layout.addWidget(self.id_label, row, 4)

        self.thread = None
        self.timer = QtCore.QTimer(parent)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update)

    def attach(self, thread):
        self.thread = thread
        self.timer.start()

        self.thread_id = id(self.thread)
        self.id_label.setText(str(self.thread_id))

        self.update()

    def update(self):
        if self.thread is None:
            self.status = "uninitialized"
        elif self.thread.isFinished():
            self.status = "halted"
        else:
            self.status = "running"
        self.status_label.setText(self.status)


class ChildWindow(QtWidgets.QDialog):
    running_position = 100

    @staticmethod
    def running_pos():
        ChildWindow.running_position += 200
        return ChildWindow.running_position

    def __init__(self, monitor, parent=None):
        super(ChildWindow, self).__init__(parent)
        monitor.attach(self.thread())
        self.label = QtWidgets.QLabel(self)
        self.label.setText(monitor.name)
        self.label.show()
        self.resize(120, 60)
        self.move(ChildWindow.running_pos(), 200)
        self.show()


class ThreadedWindow(ChildWindow):
    def __init__(self, monitor, parent=None):
        pass


class MainWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("QThread Test Application")
        self.resize(480, 360)
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        threadmonitors = ("Main Window",
                          "Child Window",
                          # "New Window",
                          "Keyboard Monitor",
                          "Clipboard Monitor",
                          "QTimer")
        self.monitors = {}
        for i in range(0, len(threadmonitors)):
            self.monitors[threadmonitors[i]] = \
                (ThreadMonitor(self, threadmonitors[i], i))
        self.layout.setRowStretch(len(self.monitors), 1)
        self.layout.setColumnMinimumWidth(1, 10)
        self.layout.setColumnMinimumWidth(3, 10)
        self.layout.setColumnStretch(5, 1)

        self.monitors["Main Window"].attach(
            QtWidgets.QApplication.instance().thread())

        self.child_window = ChildWindow(self.monitors["Child Window"], self)
        # self.new_window = ChildWindow(self.monitors["New Window"])


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # Create and show the form
    mainWindow = MainWindow()
    mainWindow.show()
    # Run the main Qt loop
    sys.exit(app.exec_())