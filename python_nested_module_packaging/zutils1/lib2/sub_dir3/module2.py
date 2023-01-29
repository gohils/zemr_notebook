#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Default python packages
import logging
import os
import time

# pip installed python packages
# from pynput.keyboard import Key, Controller

def module2_method1():
    print("module2_method1 is executed")

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
        print("login method is executed")

    def configure(self):
        """Configures file that will contain commands to run"""

        logging.info("Configuring work login")
        print("configure method is executed")


    def _run_cmd(self, cmd='default'):
        """Runs a command slowly so as not to error"""

        logging.info("_run_cmd method is executed")
        print("_run_cmd method is executed")

    def _type_key(self, key=1):
        """Types a key with a delay"""

        logging.info("_type_key method is executed")
        print("_type_key method is executed")
