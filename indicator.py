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
        self.config_action = QAction('Config')
        self.logs_action = QAction('Logs')
        self.exit_action = QAction('Exit')

        self.connect_action.triggered.connect(self._click_connect)
        self.disconnect_action.triggered.connect(self._click_disconnect)
        self.config_action.triggered.connect(self._click_config)
        self.logs_action.triggered.connect(self._click_logs)
        self.exit_action.triggered.connect(self._click_exit)

        menu.addAction(self.connect_action)
        menu.addAction(self.disconnect_action)
        menu.addSeparator()
        menu.addAction(self.config_action)
        menu.addAction(self.logs_action)
        menu.addSeparator()
        menu.addAction(self.exit_action)

        return menu

    def _click_connect(self):
        pass

    def _click_disconnect(self):
        pass

    def _click_config(self):
        pass

    def _click_logs(self):
        pass

    def _click_exit(self):
        self.app.quit()


if __name__ == '__main__':
    app = Indicator()
    app.run()