# -*- coding: utf-8 -*-
"""
    setup.py

    :copyright: (c) 2013 by Aravinda VK
    :license: BSD, GPL v2, see LICENSE for more details.
"""

from setuptools import setup, find_packages

setup(
    name = "GlusterFS Web",
    version = "0.1",
    package_dir = {"": "src"},
    packages = ["glusterfsweb"],
    include_package_data = True,
    install_requires = ['argparse'],

    entry_points = {
        "console_scripts": [
            "glusternodestate = glusterfsweb.glusternodestate:main",
            "glusterweb = glusterfsweb.glusterweb:main",
        ]
    },
    platforms = "linux",
    zip_safe=False,
    author = "Aravinda VK",
    author_email = "mail@aravindavk.in",
    description = "GlusterFS Web",
    license = "BSD, GPL v2",
    keywords = "glusterfs, web",
    url = "https://github.com/aravindavk/glusterfs-web",
)
