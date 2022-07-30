from setuptools import find_packages, setup

setup(
    name ="data_framework",
    version = "0.1.1",
    packages=find_packages(include=['utils','utils.*','redshift_module']),
)