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

import setuptools

PACKAGE_NAME = "fortivpn_quick_tray_qt"
EXECUTABLE_NAME = "ofv_qt"  # open forti vpn qt

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("%s/version" % PACKAGE_NAME, "r") as fh:
    version = fh.read()

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
    entry_points={
        "gui_scripts": [
            "%s = %s.indicator:main" % (EXECUTABLE_NAME, PACKAGE_NAME)
        ]
    }
)
