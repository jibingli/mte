#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name="mte-orm",  # pypi中的名称，pip或者easy_install安装时使用的名称
    version="1.0",
    author="li",
    author_email="run_ice_l@qq.com",
    description=("This is a api test module"),
    license="GPLv3",
    keywords="redis subscripe",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={'mte': ['*.txt'],},
    # 需要安装的依赖
    install_requires=[
        'nose', 'requests', 'sqlalchemy', 'requests_ntlm'
    ],
    zip_safe=False
)
