# Fortivpn-Quick-Tray

A simple system tray application for minitoring a `openfortivpn` connection.

Use this to connect to fortinet VPN. It uses `openfortivpn` and PySide2(Qt for Python)

# Requirements
You have to have `openfortivpn` installed on your system.

The application uses a default `config` file that should be found in the following path `/etc/openfortivpn/config`
where `config` is the file(with no `.` extention)

**fortivpn-quick-tray** does not support dynamic assignment of any arguments to `openfortivpn`. Its solemly relies on 
your *config* file. Check [openfortivpn](https://github.com/adrienverge/openfortivpn) and [man-page](https://www.mankier.com/1/openfortivpn) for options you can configure in your *config* file

# Usage
Download the latest version of the app on the [release tab](https://github.com/tshiamobhuda/fortivpn-quick-tray-qt/releases).</br>
Save the file in your desired location i.e `~/applications`.</br>
Make the application executable i.e `chmod +x fortivpn-quick-tray-qt-1.0`.</br>
Run it.</br></br>
![ftq icon](https://github.com/tshiamobhuda/fortivpn-quick-tray-qt/blob/master/icons/icon.png)</br>
Icon should appear on you System Tray.

#### Available actions
- `right-click` on the tray icon opens the logs
- `left-click` on the tray icon opens a context menu with the following items
  - `Connect` Connect to vpn. Uses `pkexec` to spwan `openfortivpn` as admin.</br>
  Disabled when there is a vpn connection
  - `Disconnect` Disconnect vpn connection. Uses `pkexec` to kill `openfortivpn` spawned by the connect process.</br>
  Disabled when there is no vpn connection
  - `Config` File chooser to select the vpn config file to be used by `openfortivpn`.</br>
  Disabled when there is a vpn connection
  - `Logs` Opens a dialog showing `openfortivpn` logs
  - `Exit` Close the app. Shows a warning dialog when there is a vpn connection.
