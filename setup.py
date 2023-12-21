# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import find_packages, setup

setup(
    name="wazo_asterisk_doc_extractor",
    version="0.0.1",
    description="Documentation extraction tool for Asterisk",
    author="Wazo Authors",
    author_email="dev@wazo.community",
    url="http://wazo.community",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "wazo-asterisk-doc-extractor = wazo_asterisk_doc_extractor.main:main",
        ],
    },
)
