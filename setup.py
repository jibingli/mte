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
    url="https://ssl.xxx.org/redmine/projects/RedisRun",
    packages=['mte','examples','test'],  # 需要打包的目录列表
    # 需要安装的依赖
    install_requires=[
        'nose', 'requests','configparser'
    ],

    # long_description=read('README.md'),
    # classifiers=[  # 程序的所属分类列表
    #     "Development Status :: 3 - Alpha",
    #     "Topic :: Utilities",
    #     "License :: OSI Approved :: GNU General Public License (GPL)",
    # ],
    # 此项需要，否则卸载时报windows error
    zip_safe=False
)
