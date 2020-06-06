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
from subprocess import check_call, check_output, call
from tempfile import TemporaryDirectory

import pkg_resources
import setuptools
from setuptools.command.install import install

PACKAGE_NAME = "fortivpn_quick_tray_qt"
EXECUTABLE_NAME = "ofv_qt"  # open forti vpn qt
DESKTOP_INSTALLER = "xdg-desktop-menu"

with open("README.md", "r") as fh:
    long_description = fh.read().strip()

with open("%s/version" % PACKAGE_NAME, "r") as fh:
    version = fh.read().strip()


class CustomInstallCommand(install):

    def __init__(self, dist):
        super().__init__(dist)
        self.has_xdg_desktop_menu = call(["which", DESKTOP_INSTALLER]) == 0

    def run(self):
        install.run(self)
        self.install_menu_item()

    def install_menu_item(self):
        """
        Installs menu item for desktop environments that implement freedesktop specs

        Expects xdg-utils to be installed.
        https://freedesktop.org/wiki/Software/xdg-utils/
        """
        if not self.has_xdg_desktop_menu:
            self.warn("%s is not installed: "
                      ".desktop file will not be installed" % DESKTOP_INSTALLER)
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
            check_call([
                "xdg-desktop-menu",
                "install",
                rendered_path
            ])
            print("Installed to start menu")


setuptools.setup(
    name="fortivpn-quick-tray-qt",
    version=version,
    author="Tshiamo Bhuda",
    description="Small simple system tray application for openfortivpn",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tshiamobhuda/fortivpn-quick-tray-qt",
    packages=setuptools.find_packages(),
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
