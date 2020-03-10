#!/usr/bin/env python3
"""
Setup script for ServiceInstaller.
"""

# Standard library imports
from pathlib import Path

# Third party imports
import setuptools


PROJECT_NAME = "serviceinstaller"


with open(Path(__file__).resolve().parent / "README.md",
          mode="r", encoding="utf-8") as readme_file:
    LONG_DESCRIPTION = readme_file.read()

# Single source the version; based on a PyPA pattern and exec is nessesary
VERSION = {}
with open(Path(__file__).resolve().parent / (PROJECT_NAME + ".py"),
          mode="r", encoding="utf-8") as version_file:
    exec(version_file.read(), VERSION)  # pylint: disable=exec-used


setuptools.setup(
    name=PROJECT_NAME,
    version=VERSION["__version__"],
    author="C.A.M. Gerlach",
    author_email="CAM.Gerlach@Gerlach.CAM",
    description=("A flexible service installer, "
                 "currently compatible with Linux Systemd."),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    keywords="systemd service linux unit installer",
    url="https://github.com/CAM-Gerlach/serviceinstaller",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Operating System",
        "Topic :: System :: Software Distribution",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        ],
    )
