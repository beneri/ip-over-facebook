from setuptools import setup
import os
import re


classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Telecommunications Industry ",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: GNU Affero General Public License v3 or "
    "later (AGPLv3+)",
    "Natural Language :: English",
    "Operating System :: Unix"
    "Programming Language :: Python :: 3.7"
]

setup(
    name='ip-over-facebook',
    version=find_version("ip-over-facebook/__init__.py"),
    author="Benjamin Eriksson, Raffaele Di Campli",
    author_email="dcdrj.pub@gmail.com",
    license='AGPLv3+',
    install_requires=[
        "requests",
        "appdirs",
        "PySide2",
        "beautifulsoup4",
        "lxml",
        "pyparsing",
        "keyring",
        "signalslot"
    ],
    python_requires='>=3.7',
    packages=['ip-over-facebook'],
    include_package_data=True,
    description="Use facebook to send data",
    classifiers=classifiers,
    entry_points={
        'console_scripts': [
            'polibeepsync=polibeepsync.qtgui:main',
        ]
    }
)
