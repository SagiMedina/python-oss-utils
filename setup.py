import os
import time
import stat
import sys
from pathlib import Path
from urllib.request import urlretrieve

import setuptools
from setuptools.command.install import install

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()
with open('VERSION') as version_file:
    version = version_file.read().strip()
with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()


def _reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    if count % 20 != 0:
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write(
        "\r...%d%%, %d MB, %d KB/s, %d seconds passed"
        % (percent, progress_size / (1024 * 1024), speed, duration)
    )
    sys.stdout.flush()


class InstallWrapper(install):

    def run(self):
        install.run(self)
        self.download_oss_util()

    def download_oss_util(self):
        # Current version: 1.7.0
        print("Downloading OSSUtil...")
        ossutil_url = None
        if sys.platform.startswith("linux"):
            ossutil_url = "https://gosspublic.alicdn.com/ossutil/1.7.0/ossutil64?spm=a2c63.p38356.879954.6.427a24541x9Gcv"
        if sys.platform.startswith("darwin"):
            ossutil_url = "https://gosspublic.alicdn.com/ossutil/1.7.0/ossutilmac64?spm=a2c63.p38356.879954.10.427a24541x9Gcv"
        if ossutil_url is not None:
            ossutil_folder = Path(self.install_lib, "python_oss_utils")
            ossutil_folder.mkdir(parents=True, exist_ok=True)
            ossutil_path = Path(ossutil_folder, "ossutil")
            urlretrieve(ossutil_url, ossutil_path, reporthook=_reporthook)
            st = os.stat(ossutil_path)
            os.chmod(ossutil_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


setuptools.setup(
    name="python-oss-utils",
    version=version,
    author="Alibaba Inc.",
    description="OSS SDK wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SagiMedina/python-oss-utils",
    packages=setuptools.find_packages(exclude=['tests']),
    cmdclass={'install': InstallWrapper},
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)