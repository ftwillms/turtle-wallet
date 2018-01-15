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


signal.signal(signal.SIGINT, signal.SIG_DFL) # Required to handle interrupts closing the program
splash_screen = SplashScreen() # Create a new instance of the splash screen

# Make sure the splash screen wasn't cancelled by the user
if not splash_screen.startup_cancelled:
    Gtk.main() # Start the main GTK loop

if global_variables.wallet_connection:
    global_variables.wallet_connection.stop_wallet_daemon()
