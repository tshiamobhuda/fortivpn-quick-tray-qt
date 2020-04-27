#!/usr/bin/python

from sys import exit as sys_exit
from PySide2.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PySide2.QtGui import QIcon

class Indicator():
    def __init__(self):
        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)
        self.indicator = QSystemTrayIcon()
        self.indicator.setIcon(QIcon('icons/off.png'))
        self.indicator.setContextMenu(self._build_menu())
        self.indicator.setVisible(True)

    def run(self):
        self.app.exec_()
        sys_exit()

    def _build_menu(self):
        menu = QMenu()

        self.connect_action = QAction('Connect')
        self.disconnect_action = QAction('Diconnect')
        self.config_action = QAction('Confug')
        self.logs_action = QAction('Logs')
        self.exit_action = QAction('Exit')

        self.exit_action.triggered.connect(self.app.quit)

        menu.addAction(self.connect_action)
        menu.addAction(self.disconnect_action)
        menu.addAction(self.config_action)
        menu.addAction(self.logs_action)
        menu.addAction(self.exit_action)

        return menu


if __name__ == '__main__':
    app = Indicator()
    app.run()