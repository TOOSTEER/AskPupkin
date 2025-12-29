#!/usr/bin/env python
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="ask_pupkin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    description="Q&A platform similar to Stack Overflow",
    author="Student",
    python_requires=">=3.9",
)