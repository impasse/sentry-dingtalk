#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from multiprocessing import util


tests_require = [
]

install_requires = [
    'sentry>=9.0.0',
    'redis-py-cluster==1.3.4'
]

setup(
    name='sentry-dingtalk',
    version='1.0.0',
    author='shyling',
    author_email='i@uuz.io',
    url='https://github.com/impasse/sentry-dingtalk',
    description='A Sentry extension integrates with Dingtalk webhook.',
    long_description=__doc__,
    license='BSD',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.collector',
    entry_points={
        'sentry.plugins': [
            'dingtalk = sentry_dingtalk.plugin:DingtalkPlugin'
        ],
    },
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
