"""This module sets up the package """

from setuptools import find_packages, setup

setup(
    name ="data_framework",
    version = "0.1.1",
    packages=find_packages(),
# this entry_points are shortcuts can be called directly after pip install data_framework from command line      
    entry_points={
        'console_scripts': [
            'run_mod2 = zutils1.lib1.mod2:module2_method1',
            'run_mod4 = zutils2.lib2.transform1:module4_method1',
        ]}
)
