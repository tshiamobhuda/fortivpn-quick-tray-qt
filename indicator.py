#!/usr/bin/python

import sys
from os import remove as remove_log_file, path
from PySide2.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QFileDialog, QTextEdit, QMessageBox
from PySide2.QtGui import QIcon
from PySide2.QtCore import QThread, QObject, Signal, Slot
from time import sleep
from shlex import split
from threading import Thread
from subprocess import Popen, PIPE, TimeoutExpired, run
from tempfile import NamedTemporaryFile

class Indicator():
    APP_NAME = 'FortiVPN Quick Tray'

    def __init__(self):
        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)
        self.indicator = QSystemTrayIcon()
        self.indicator.setIcon(QIcon(self._get_file('./icons/icon.png')))
        self.indicator.setContextMenu(self._build_menu())
        self.indicator.setVisible(True)
        self.indicator.setToolTip('OFF')
        
        self.indicator.activated.connect(self._click_indicator)

        self.logs_dialog = QTextEdit()
        self.logs_dialog.setWindowTitle(f'{self.APP_NAME} - Logs')
        self.logs_dialog.setFixedSize(440, 440)
        self.logs_dialog.setReadOnly(True)
        self.logs_dialog.setWindowIcon(QIcon(self._get_file('./icons/icon.png')))
        
        self.vpn_config = '/etc/openfortivpn/config'
        self.vpn_process = None
        self.vpn_logs_file = NamedTemporaryFile(delete=False)
        
        self.vpn_thread = VPNThread(self.vpn_logs_file)
        self.vpn_thread.vpn_status.connect(self._update_vpn_status)

    def run(self):
        self.app.exec_()
        sys.exit()

    def _build_menu(self):
        menu = QMenu()

        self.connect_action = QAction('Connect')
        self.disconnect_action = QAction('Disconnect')
        self.config_action = QAction('Config')
        self.logs_action = QAction('Logs')
        self.exit_action = QAction('Exit')

        self.disconnect_action.setDisabled(True)

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
        self.indicator.setIcon(QIcon(self._get_file('./icons/try.png')))
        self.indicator.setToolTip('TRYING')

        self.connect_action.setDisabled(True)
        self.config_action.setDisabled(True)

        with open(self.vpn_logs_file.name, 'w+b') as f:
            try:
                self.vpn_process = Popen(split('pkexec openfortivpn -c ' + self.vpn_config), stdin=PIPE, stdout=f, stderr=f)
                self.vpn_process.communicate(timeout=1)
            except TimeoutExpired:
                pass

        self.vpn_thread.start()

    def _click_disconnect(self):
        try:
            run(split('pkexec kill ' + str(self.vpn_process.pid)))
        except ChildProcessError:
            pass

    def _click_config(self):
        config_file, _ = QFileDialog.getOpenFileName(
            caption='Select config file',
            dir='/',
            filter='All files (*)',
            options=QFileDialog.DontUseNativeDialog
        )

        if config_file:
            self.vpn_config = config_file

    def _click_logs(self):
        with open(self.vpn_logs_file.name) as logs:
            self.logs_dialog.setPlainText(logs.read())

        self.logs_dialog.show()

    def _click_exit(self):
        if self.indicator.toolTip() == 'ON':
            _ = QMessageBox.warning(None, self.APP_NAME, 'VPN is still ON. Please Disconnect first before exiting')

            return

        if self.vpn_logs_file.name:
            remove_log_file(self.vpn_logs_file.name)

        self.app.quit()

    def _get_file(self, file_path):
        try:
            base = sys._MEIPASS
        except Exception:
            base = path.abspath('.')

        return path.join(base, file_path)

    def _click_indicator(self, event):
        if event == QSystemTrayIcon.ActivationReason.Trigger:
            self._click_logs()

    def _update_vpn_status(self, message):
        if message == 'ERR':
            self.indicator.setIcon(QIcon(self._get_file('./icons/err.png')))
            self.indicator.setToolTip('ERROR')
            self.connect_action.setDisabled(False)
            self.config_action.setDisabled(False)
            pass

        if message == 'ON':
            self.indicator.setIcon(QIcon(self._get_file('./icons/on.png')))
            self.indicator.setToolTip('ON')
            self.disconnect_action.setDisabled(False)
            pass

        if message == 'OFF':
            self.indicator.setIcon(QIcon(self._get_file('./icons/icon.png')))
            self.indicator.setToolTip('OFF')
            self.disconnect_action.setDisabled(True)
            self.connect_action.setDisabled(False)
            self.config_action.setDisabled(False)
            pass


class VPNThread(QThread):
    vpn_status = Signal(str)

    def __init__(self, vpn_logs_file=None):
        super().__init__(None)

        self.vpn_logs_file = vpn_logs_file

    def run(self):
        with open(self.vpn_logs_file.name) as f:
            while True:
                line = f.readline()
                if line.find('Error') != -1 or line.find('ERROR') != -1:
                    self.vpn_status.emit('ERR')
                    break

                if line.find('Tunnel is up and running') != -1:
                    self.vpn_status.emit('ON')
                    pass

                if line.find('Logged out') != -1:
                    self.vpn_status.emit('OFF')
                    break

                self.sleep(0.1)


if __name__ == '__main__':
    app = Indicator()
    app.run()
