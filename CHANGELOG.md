## [1.1.0] - 2020-05-20
### Added
- auto update checker which checks for an update when the app is launched.
### Changed
- logs to auto update while logs are being viewed.

## [1.0.1] - 
### Fixed
- typo on menu item, [typo]: Diconnect -> [fix]: Disconnect

## [1.0.0]
Initial Release of FortiVPN Quick Tray
### Added
- system tray icon with minimal FQT icon shown when vpn connection is inactive
- menu items to connect, disconnect, config, view log, and exit the application
- usage of pkexec to run openfortivpn in separate thread as su
- showing of appropriate icon when VPN is connected or an Error is encounter
- viewing of logs from the openfortivpn stream out
