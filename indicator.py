#!/usr/bin/python

from sys import exit as sys_exit
from PySide2.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QFileDialog, QTextEdit, QMessageBox
from PySide2.QtGui import QIcon
from time import sleep
from shlex import split
from threading import Thread
from subprocess import Popen, PIPE, TimeoutExpired, run

class Indicator():
    APP_NAME = 'FortiVPN Quick Tray'

    def __init__(self):
        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)
        self.indicator = QSystemTrayIcon()
        self.indicator.setIcon(QIcon('icons/off.png'))
        self.indicator.setContextMenu(self._build_menu())
        self.indicator.setVisible(True)
        self.indicator.setToolTip('OFF')

        self.logs_dialog = QTextEdit()
        self.logs_dialog.setWindowTitle(self.APP_NAME)
        self.logs_dialog.setFixedSize(440, 440)
        self.logs_dialog.setReadOnly(True)
        
        self.vpn_config = '/etc/openfortivpn/config'
        self.vpn_process = None

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
        self.indicator.setIcon(QIcon('icons/try.png'))
        self.indicator.setToolTip('TRY')

        self.connect_action.setDisabled(True)
        self.config_action.setDisabled(True)

        with open('output.log', 'w+b') as f:
            try:
                self.vpn_process = Popen(split('pkexec openfortivpn -c ' + self.vpn_config), stdin=PIPE, stdout=f, stderr=f)
                self.vpn_process.communicate(timeout=1)
            except TimeoutExpired:
                pass
        
        vpn_process_thread = Thread(target=self._monitor_logs, daemon=True)
        vpn_process_thread.start()

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
        self.logs_dialog.show()

    def _click_exit(self):
        if self.indicator.toolTip() == 'ON':
            QMessageBox.warning(title=self.APP_NAME, text='VPN is still ON. Please Disconnect first before exiting')

            return

        self.app.quit()

    def _monitor_logs(self):
        with open('output.log') as f:
            while True:
                line = f.readline()
                if line.find('Error') != -1 or line.find('ERROR') != -1:
                    self.indicator.setIcon(QIcon('icons/err.png'))
                    self.indicator.setToolTip('ERR')
                    self.connect_action.setDisabled(False)
                    self.config_action.setDisabled(False)
                    break

                if line.find('Tunnel is up and running') != -1:
                    self.indicator.setIcon(QIcon('icons/on.png'))
                    self.indicator.setToolTip('ON')
                    self.disconnect_action.setDisabled(False)


                if line.find('Logged out') != -1:
                    self.indicator.setIcon(QIcon('icons/off.png'))
                    self.indicator.setToolTip('OFF')
                    self.disconnect_action.setDisabled(True)
                    self.connect_action.setDisabled(False)
                    self.config_action.setDisabled(False)
                    break

                sleep(0.1)

if __name__ == '__main__':
    app = Indicator()
    app.run()