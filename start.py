# -*- coding: utf-8 -*-
""" start.py

This file launches the wallet and starts the main GTK loop.
"""

import global_variables

import signal
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from SplashScreen import SplashScreen

import argparse
import os


signal.signal(signal.SIGINT, signal.SIG_DFL) # Required to handle interrupts closing the program
splash_screen = SplashScreen() # Create a new instance of the splash screen
Gtk.main() # Start the main GTK loop

if global_variables.wallet_connection:
    global_variables.wallet_connection.stop_wallet_daemon()
