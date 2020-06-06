"""
fortivpn-quick-tray-qt
MIT License

Copyright (c) 2020 LoveIsGrief

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
from distutils import log
from subprocess import check_output, call, run, PIPE, CalledProcessError
from tempfile import TemporaryDirectory

import pkg_resources
import setuptools
from setuptools.command.install import install

NAME = "fortivpn-quick-tray-qt"
PACKAGE_NAME = NAME.replace("-", "_")
EXECUTABLE_NAME = "ofv_qt"  # open forti vpn qt
DESKTOP_INSTALLER = "xdg-desktop-menu"
ICON_INSTALLER = "xdg-icon-resource"
ICON_SIZE = 32

with open("README.md", "r") as fh:
    long_description = fh.read().strip()

with open("%s/version" % PACKAGE_NAME, "r") as fh:
    version = fh.read().strip()


def call_with_exception(cmd_list):
    run(cmd_list, stdout=PIPE, stderr=PIPE, check=True)


class CustomInstallCommand(install):

    def __init__(self, dist):
        super().__init__(dist)
        self.has_xdg_desktop_menu_cmd = call(["which", DESKTOP_INSTALLER]) == 0
        self.has_xdg_icon_resource_cmd = call(["which", ICON_INSTALLER]) == 0

    def run(self):
        install.run(self)
        try:
            self.install_menu_item()
        except Exception as exception:
            self.announce("Couldn't install menu item: %s" % exception, log.ERROR)
            self.check_for_call_error(exception)

        try:
            self.install_menu_icon()
        except Exception as exception:
            self.announce("Couldn't install menu icon: %s" % exception, log.ERROR)
            self.check_for_call_error(exception)

    def check_for_call_error(self, error):
        if not isinstance(error, CalledProcessError):
            return
        if error.stdout:
            self.announce("Command stdout: %s" % error.stdout.decode(), log.ERROR)
        if error.stderr:
            self.announce("Command stderr: %s" % error.stderr.decode(), log.ERROR)

    def install_menu_item(self):
        """
        Installs menu item for desktop environments that implement freedesktop specs

        Expects xdg-utils to be installed.
        https://freedesktop.org/wiki/Software/xdg-utils/
        """
        if not self.has_xdg_desktop_menu_cmd:
            self.warn("%s is not installed: "
                      "menu entry will not be installed" % DESKTOP_INSTALLER)
            return

        template_name = "fortivpn-quick-tray-qt.desktop"
        template_path = pkg_resources.resource_filename(
            PACKAGE_NAME, "/templates/%s" % template_name
        )
        with TemporaryDirectory() as tempdir_name:
            rendered_path = os.path.join(tempdir_name, template_name)

            # Find where the script was installed
            # returns a bytes object hence the decode
            executable_path = check_output(["which", EXECUTABLE_NAME]).decode().strip()

            # Generate .desktop file
            with open(template_path, 'r') as template_file, open(rendered_path, 'w') as tempfile:
                template = template_file.read()
                tempfile.write(template.format(executable=executable_path))

            # Install the desktop file
            call_with_exception([
                "xdg-desktop-menu",
                "install",
                rendered_path
            ])
        self.announce("Installed start menu entry", log.INFO)

    def install_menu_icon(self):
        if not self.has_xdg_icon_resource_cmd:
            self.warn("%s is not installed: "
                      "menu icon will not be installed" % ICON_INSTALLER)
            return

        # Install the icon to freedesktop
        call_with_exception([
            ICON_INSTALLER,
            "install",
            "--size",
            str(ICON_SIZE),
            pkg_resources.resource_filename(PACKAGE_NAME, "icons/icon.png"),
            NAME
        ])
        self.announce("Installed start menu icon", log.INFO)


setuptools.setup(
    name=NAME,
    version=version,
    author="Tshiamo Bhuda",
    description="Small simple system tray application for openfortivpn",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tshiamobhuda/fortivpn-quick-tray-qt",
    packages=setuptools.find_packages(),
    install_requires=[
        "PySide2>=5.14.0",
    ],
    package_data={
        PACKAGE_NAME: [
            "version",
            "icons/*.png",
            "templates/*"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Topic :: Desktop Environment :: K Desktop Environment (KDE)",
        "Topic :: Desktop Environment :: Gnome",
        "Topic :: System :: Networking"
    ],
    python_requires='>=3.6',
    cmdclass={
        "install": CustomInstallCommand
    },
    entry_points={
        "gui_scripts": [
            "%s = %s.indicator:main" % (EXECUTABLE_NAME, PACKAGE_NAME)
        ]
    }
)
