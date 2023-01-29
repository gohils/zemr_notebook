#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Default python packages
import logging
import os
import time

# pip installed python packages
# from pynput.keyboard import Key, Controller

def module4_method1():
    print("module4_method1 is executed")

class Module2Class2:
    """Class that performs functions for login"""

    def __init__(self, conf_path=os.path.join(os.path.expanduser("~"),
                                              ".work_login.conf")):
        """Saves config file location"""

        self.conf_path = conf_path
        self.keyboard = 'Controller()'

    def login(self):
        """Logs user in through terminal"""

        # Configures config file if not done so already
        print("module4 login method is executed")

    def configure(self):
        """Configures file that will contain commands to run"""

        logging.info("module4 Configuring work login")
        print("module4 configure method is executed")


    def _run_cmd(self, cmd='default'):
        """Runs a command slowly so as not to error"""

        logging.info("module4 _run_cmd method is executed")
        print("module4 _run_cmd method is executed")


