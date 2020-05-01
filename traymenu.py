"""
This module handles the tray icon, the right click context menu,
and the global settings menu. The modus menu is handled by the modus file.

Signals emitted:
app_shutdown_now(): halt all threads, close all windows, save settings.
modus_menu_opened(): instructs modus to open individual settings window.
new_modus_loaded(Modus): emits a copy of the new modus to be instantiated over the
        old modus. also tells that old modus to deconstruct

"""

import sys
import zipimport
import os.path

from PySide2 import QtGui, QtWidgets, QtCore
from PySide2.QtCore import Signal, Slot

from basemodus import Modus


def load_modus(path):
    importer = zipimport.zipimporter(path)
    modus_name = os.path.splitext(os.path.basename(path))[0]
    modus_module = importer.load_module(modus_name)
    modus = getattr(modus_module, modus_name)()
    return modus


class GenericMenu(QtWidgets.QDialog):
    """
    A generic window class to handle common options for all windows generated
    by the top level application
    """
    def __init__(self, parent=None):
        super(GenericMenu, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() &
                            ~QtCore.Qt.WindowContextHelpButtonHint)


class ConfigWindow(GenericMenu):
    """
    The main configuration/options page for the app.
    Modus-specific settings are handled by the modus itself.
    """
    def __init__(self, parent=None):
        super(ConfigWindow, self).__init__(parent)

        self.label = QtWidgets.QLabel(self)
        self.label.setText("Sylladex System Settings")
        self.label.show()
        self.resize(200, 100)

        self.show()


class LoaderWindow(QtWidgets.QFileDialog):
    """
    A file finder dialog for loading a new modus file.
    """
    def __init__(self, parent=None):
        super(LoaderWindow, self).__init__(parent)

        # self.setWindowFlags(self.windowFlags() &
        #                     ~QtCore.Qt.WindowContextHelpButtonHint)

    def get_modus_path(self):
        self.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        self.setNameFilter("Modus Files (*.modus)")
        self.setViewMode(QtWidgets.QFileDialog.Detail)
        self.open()


class AboutWindow(GenericMenu):
    """
    A simple about page for the application.
    """
    def __init__(self, parent=None):
        super(AboutWindow, self).__init__(parent)

        self.label = QtWidgets.QLabel(self)
        self.label.setText("About this application!\r\n\r\n8^y")
        #TODO
        self.label.show()
        self.resize(200, 100)

        self.show()


class TrayIcon(QtWidgets.QSystemTrayIcon):
    """
    TrayIcon manages the system tray icon and has most of the "guts" of the tray
    application. This manages communication with sub windows, and because
    it's the most persistent window, does a lot of top-level application
    management.
    """

    app_shutdown_now = Signal()
    modus_menu_opened = Signal()
    new_modus_loaded = Signal(Modus)

    def __init__(self, parent=None):
        self.icon = QtGui.QIcon("tray.png")
        QtWidgets.QSystemTrayIcon.__init__(self, self.icon, parent)
        self.show()

        menu = QtWidgets.QMenu(parent)

        self.child_window = None
        #TODO: add dividers, clean this up
        menu_action = menu.addAction("Configure Sylladex")
        menu_action.triggered.connect(self.open_config)
        menu_action = menu.addAction("Load Fetch Modus")
        menu_action.triggered.connect(self.open_load)
        menu_action = menu.addAction("About")
        menu_action.triggered.connect(self.open_about)
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.tray_exit)

        self.activated.connect(self.handle_clicks)
        self.setContextMenu(menu)

    def tray_exit(self):
        self.hide()
        self.app_shutdown_now.emit()
        QtCore.QCoreApplication.instance().quit()

    def _switch_menu(self, menutype):
        if self.child_window is None:
            self.child_window = menutype(self.parent())
        else:
            if self.child_window is not menutype:
                self.child_window.close()
                self.child_window = menutype(self.parent())
        return self.child_window

    def open_config(self):
        self._switch_menu(ConfigWindow)

    def open_load(self):
        file_select = self._switch_menu(LoaderWindow)
        file_select.fileSelected.connect(self.load_modus)
        file_select.get_modus_path()

    @Slot()
    def load_modus(self, filepath):
        modus = load_modus(filepath)
        self.new_modus_loaded.emit(modus)
        #TODO: update the icon based on color of loaded modus :)

    def open_about(self):
        self._switch_menu(AboutWindow)

    def handle_clicks(self, reason):
        if reason.name == b'Trigger':
            self.modus_menu_opened.emit()


class TrayApp(QtWidgets.QWidget):
    """
    QT doesn't let the parent of a qwidget be a qobject, so we can't
    have TrayIcon be the parent of any menus. This is a wrapper class
    to serve as that common parent for all user menus.
    """

    def __init__(self, parent=None):
        super(TrayApp, self).__init__(parent)

        self.tray = TrayIcon(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    tray = TrayApp()

    sys.exit(app.exec_())
