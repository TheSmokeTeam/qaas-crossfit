#!/usr/bin/env python
"""Crossfit package builder and installer"""
import glob
import os
import sys
import io

import setuptools


def project_setup():
    package_name = 'crossfit'
    short_description = 'Crossfit package for modularity of coverage tools'

    try:
        with io.open('README.md', encoding='utf-8') as strm:
            long_description = strm.read()
    except Exception:
        long_description = short_description

    classifiers = [
        'Intended Audience :: QA teams and Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ]

    author = "REDA"
    author_email = 'REDA'
    url = "REDA/crossfit.git"
    packages = setuptools.find_packages(include=["crossfit", "crossfit.*", ])

    needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
    pytest_runner = ['pytest_runner'] if needs_pytest else []

    extra_files = [os.path.relpath(f) for f in glob.glob(r"crossfit/bin/**/*", recursive=True) if os.path.isfile(f)]

    try:
        with io.open('requirements.txt') as f:
            install_require = [l.strip() for l in f.readlines() if not l.startswith('#')]
    except Exception:
        install_require = []

    setuptools.setup(
        name=package_name,
        version=f"{os.getenv('ARTIFACT_VERSION_TAG')}",
        description=short_description,
        long_description=long_description,

        author=author,
        author_email=author_email,
        url=url,

        classifiers=classifiers,
        packages=packages,
        include_package_data=True,
        package_data={"crossfit": extra_files},
        install_requires=install_require,
        python_requires='>=3.8',
        setup_requires=pytest_runner,
        zip_safe=False
    )


def main():
    """Package installation entry point."""
    project_setup()


if __name__ == '__main__':
    main()
