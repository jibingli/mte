#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

setup(
    name="mte-orm",  # pypi中的名称，pip或者easy_install安装时使用的名称
    version="1.0",
    author="li",
    author_email="run_ice_l@qq.com",
    description=("This is a api test module"),
    license="GPLv3",
    keywords="redis subscripe",
    packages=['mte'],  # 需要打包的目录列表
    # 需要安装的依赖
    install_requires=[
        'nose', 'requests','sqlalchemy'
    ],
    zip_safe=False
)
