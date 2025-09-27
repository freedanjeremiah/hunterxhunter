#!/usr/bin/env python3
"""
Setup configuration for walrus-git-cli
Professional packaging for Walrus Git CLI - Git-like interface for Walrus storage
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = ""
readme_path = this_directory / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    requirements = requirements_path.read_text().splitlines()
    # Filter out comments and empty lines
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="walrus-git-cli",
    version="1.0.0",
    author="Walrus Developer",
    author_email="developer@walrus.storage",
    description="Git-like CLI for Walrus decentralized storage with push/pull functionality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/walrus-storage/walrus-git-cli",
    project_urls={
        "Bug Tracker": "https://github.com/walrus-storage/walrus-git-cli/issues",
        "Documentation": "https://docs.walrus.storage/",
        "Source Code": "https://github.com/walrus-storage/walrus-git-cli",
    },
    packages=find_packages(exclude=["tests", "tests.*", "publisher", "publisher.*"]),
    py_modules=['walrus_cli'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: System :: Archiving",
        "Topic :: Software Development :: Version Control",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
        ],
        "publisher": [
            "PyYAML>=6.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "walrus=walrus_cli:main",
            "walrus-push=walrus_cli:main_push", 
            "walrus-pull=walrus_cli:main_pull",
            "walrus-list=walrus_cli:main_list",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="walrus storage git cli decentralized blockchain",
    license="MIT",
)