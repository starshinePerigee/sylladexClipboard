import sys
from PySide2 import QtGui, QtWidgets, QtCore


class AnimationIndicator(QtWidgets.QLabel):
    def __init__(self, parent, startpos, endpos):
        super(AnimationIndicator, self).__init__(parent)
        self.setText("<>")
        self.show()
        # noinspection PyTypeChecker
        self.moveAni = QtCore.QPropertyAnimation(self, b"pos")
        self.moveAni.setDuration((endpos-startpos).manhattanLength()*8)
        self.moveAni.setStartValue(startpos)
        self.moveAni.setKeyValueAt(0.5, endpos)
        self.moveAni.setEndValue(startpos)
        self.moveAni.setLoopCount(-1)
        self.moveAni.start()


class ChildWindow(QtWidgets.QDialog):
    def __init__(self, caller, parent=None):
        super(ChildWindow, self).__init__(parent)
        self.caller = caller
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Child window!")
        self.label.show()
        self.resize(200, 100)

        self.aniLabel = AnimationIndicator(self,
                                           QtCore.QPoint(0, 80),
                                           QtCore.QPoint(180, 80))

        self.show()
        self.caller.is_menu_visible = True

    def closeEvent(self, event):
        self.caller.is_menu_visible = False


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtWidgets.QMenu(parent)

        self.child_window = None
        self.is_menu_visible = False
        menu_action = menu.addAction("Toggle Menu")
        menu_action.triggered.connect(self.toggle_menu)
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.tray_exit)

        self.activated.connect(self.handle_clicks)
        self.setContextMenu(menu)

    def tray_exit(self):
        self.hide()
        QtCore.QCoreApplication.instance().quit()

    def toggle_menu(self):
        if not self.is_menu_visible:
            self.child_window = ChildWindow(self)
        else:
            self.child_window.close()

    @staticmethod
    def handle_clicks(reason):
        print(reason.name)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    tray_icon = TrayIcon(QtGui.QIcon("tray.png"))
    tray_icon.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
