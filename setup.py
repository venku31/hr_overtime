from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in hr_overtime/__init__.py
from hr_overtime import __version__ as version

setup(
	name="hr_overtime",
	version=version,
	description="HR Overtime",
	author="Venkatesh",
	author_email="vn2019453@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
