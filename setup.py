#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import pathlib
import subprocess
from setuptools import setup

from nautiluszim.constants import NAME, VERSION

ROOT_DIR = pathlib.Path(__file__).parent

with open(ROOT_DIR.joinpath("requirements.txt"), "r") as fp:
    requirements = [
        line.strip() for line in fp.readlines() if not line.strip().startswith("#")
    ]

with open(ROOT_DIR.joinpath("README.md"), "r") as fp:
    long_description = fp.read()

print("Downloading and fixing JS dependencies...")
ps = subprocess.run(["/bin/bash", str(ROOT_DIR.joinpath("get_js_deps.sh"))])
ps.check_returncode()


setup(
    name=NAME,
    version=VERSION,
    description="turns a collection of documents into a browsable ZIM file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="kiwix",
    author_email="reg@kiwix.org",
    url="https://github.com/openzim/nautilus",
    keywords="kiwix zim offline",
    license="GPLv3+",
    packages=["nautiluszim"],
    install_requires=requirements,
    zip_safe=False,
    platforms="Linux",
    include_package_data=True,
    entry_points={"console_scripts": ["nautiluszim=nautiluszim.__main__:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    python_requires=">=3.6",
)
