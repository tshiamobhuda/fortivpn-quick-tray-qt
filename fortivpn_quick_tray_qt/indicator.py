#!/usr/bin/python3

import sys
import json
from os import remove as remove_log_file, path

import pkg_resources
from PySide2.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QFileDialog, QTextEdit, QMessageBox
from PySide2.QtGui import QIcon
from PySide2.QtCore import QThread, Signal
from shlex import split
from subprocess import Popen, PIPE, TimeoutExpired, run
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from urllib.error import HTTPError
from distutils.version import StrictVersion

SCRIPT_DIR = path.dirname(__file__)


def _get_file(rel_path):
    return pkg_resources.resource_filename(__name__, rel_path)


class Indicator():
    APP_NAME = 'FortiVPN Quick Tray'

    def __init__(self):
        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)
        self.indicator = QSystemTrayIcon()
        self.indicator.setIcon(QIcon(_get_file('icons/icon.png')))
        self.indicator.setContextMenu(self._build_menu())
        self.indicator.setVisible(True)
        self.indicator.setToolTip('OFF')

        self.indicator.activated.connect(self._click_indicator)

        self.logs_dialog = QTextEdit()
        self.logs_dialog.setWindowTitle(f'{self.APP_NAME} - Logs')
        self.logs_dialog.setFixedSize(440, 440)
        self.logs_dialog.setReadOnly(True)
        self.logs_dialog.setWindowIcon(QIcon(_get_file('icons/icon.png')))

        self.vpn_config = '/etc/openfortivpn/config'
        self.vpn_process = None
        self.vpn_logs_file = NamedTemporaryFile(delete=False)

        self.vpn_thread = VPNThread(self.vpn_logs_file)
        self.vpn_thread.status.connect(self._update_vpn_status)
        self.vpn_thread.log.connect(self.logs_dialog.append)

        self.app_update_thread = AppUpdateThread(_get_file('version'))
        self.app_update_thread.update_available.connect(self._show_update_notification)
        self.app_update_thread.start()

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
        self.indicator.setIcon(QIcon(_get_file('icons/try.png')))
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
        if not self.vpn_thread.isRunning():
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

    def _click_indicator(self, event):
        if event == QSystemTrayIcon.ActivationReason.Trigger:
            self._click_logs()

    def _update_vpn_status(self, message):
        if message == 'ERR':
            self.indicator.setIcon(QIcon(_get_file('icons/err.png')))
            self.indicator.setToolTip('ERROR')
            self.connect_action.setDisabled(False)
            self.config_action.setDisabled(False)
            pass

        if message == 'ON':
            self.indicator.setIcon(QIcon(_get_file('icons/on.png')))
            self.indicator.setToolTip('ON')
            self.disconnect_action.setDisabled(False)
            pass

        if message == 'OFF':
            self.indicator.setIcon(QIcon(_get_file('icons/icon.png')))
            self.indicator.setToolTip('OFF')
            self.disconnect_action.setDisabled(True)
            self.connect_action.setDisabled(False)
            self.config_action.setDisabled(False)
            pass

    def _show_update_notification(self, flag):
        if flag and self.indicator.supportsMessages:
            self.indicator.showMessage(self.APP_NAME, 'There is a new update available', QIcon(_get_file(
                'icons/icon.png')))


class VPNThread(QThread):
    status = Signal(str)
    log = Signal(str)

    def __init__(self, vpn_logs_file):
        super().__init__(None)

        self.vpn_logs_file = vpn_logs_file

    def run(self):
        with open(self.vpn_logs_file.name) as f:
            while True:
                line = f.readline()

                if len(line) > 0:
                    self.log.emit(line.rstrip())

                if line.find('Error') != -1 or line.find('ERROR') != -1:
                    self.status.emit('ERR')
                    break

                if line.find('Tunnel is up and running') != -1:
                    self.status.emit('ON')

                if line.find('Logged out') != -1:
                    self.status.emit('OFF')
                    break

                self.sleep(0.1)

class AppUpdateThread(QThread):
    update_available = Signal(bool)

    def __init__(self, version_file):
        super().__init__(None)

        self.version_file = version_file

    def run(self):
        try:
            response = urlopen('https://api.github.com/repos/tshiamobhuda/fortivpn-quick-tray-qt/releases/latest')
            release = json.loads(response.read().decode())
        except HTTPError:
            return

        with open(self.version_file) as f:
            current = f.read()

        if StrictVersion(release.get('tag_name')) > StrictVersion(current):
            self.update_available.emit(True)

            return

        self.update_available.emit(False)


if __name__ == '__main__':
    app = Indicator()
    app.run()
