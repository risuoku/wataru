from setuptools import (
    setup,
    find_packages,
)
import importlib

_version = importlib.import_module('wataru').__version__
EXCLUDE_FROM_PACKAGES = []

setup (
    name='wataru',
    version=_version,
    author='risuoku',
    author_email='risuo.data@gmail.com',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'wataru = wataru.commands:execute_from_argument',
        ]
    }
)
