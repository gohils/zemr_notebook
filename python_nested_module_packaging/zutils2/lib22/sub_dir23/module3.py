#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Default python packages
import logging
import os
import time

# pip installed python packages
# from pynput.keyboard import Key, Controller


class Module3Class1:
    """Class that performs functions for login"""

    def __init__(self, conf_path=os.path.join(os.path.expanduser("~"),
                                              ".work_login.conf")):
        """Saves config file location"""

        self.conf_path = conf_path
        self.keyboard = 'Controller()'

    def configure(self):
        """Configures file that will contain commands to run"""

        logging.info("Configuring the module3")
        print("module3 -class method configure is executed")


    def _run_cmd(self, cmd='default'):
        """Runs a command slowly so as not to error"""

        logging.info("module3 - _run_cmd method is executed")
        print("module3 - class method _run_cmd is executed")
