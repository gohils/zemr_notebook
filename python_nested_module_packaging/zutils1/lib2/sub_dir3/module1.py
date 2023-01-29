#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Default python packages
import logging
import os
import time

# pip installed python packages
# from pynput.keyboard import Key, Controller


class Module1Class1:
    """Class that performs functions for login"""

    def __init__(self, conf_path=os.path.join(os.path.expanduser("~"),
                                              ".work_login.conf")):
        """Saves config file location"""

        self.conf_path = conf_path
        self.keyboard = 'Controller()'

    def configure(self):
        """Configures file that will contain commands to run"""

        logging.info("Module1 Configuring the module1")
        print("Module1 class method configure is executed")


    def _run_cmd(self, cmd='default'):
        """Runs a command slowly so as not to error"""

        logging.info("Module1 _run_cmd method is executed")
        print("Module1 class method _run_cmd is executed")
