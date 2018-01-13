# -*- coding: utf-8 -*-
""" global_variables.py

This file stores the global variables for the wallet.
"""
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# The main wallet connection object that handles communicating
# to the wallet daemon process and talking to the RPC server.
wallet_connection = None

