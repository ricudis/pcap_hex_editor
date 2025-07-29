#!/usr/bin/env python3
"""
Setup script for HexyVibe PCAP Hex Editor
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    return "A PCAP Hex Editor with Textual UI"

# Read requirements
def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

setup(
    name="pcap_hex_editor",
    version="1.0.0",
    author="Christos Rikoudis",
    author_email="ricudis.christos@gmail.com",
    description="A PCAP Hex Editor with Textual UI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "pcap-hex-editor=pcap_hex_editor.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pcap_hex_editor": ["data/*.pcap"],
    },
    keywords="pcap, hex, editor, network, packets, scapy, textual",
    project_urls={
        "Bug Reports": "",
        "Source": "",
    },
) 