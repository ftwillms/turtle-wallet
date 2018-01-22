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
import logging

# create logger for entire wallet application
logger = logging.getLogger('trtl_log')
logger.setLevel(logging.DEBUG)
# create handle to log file that will hold all events
fh = logging.FileHandler('trtl.log')
fh.setLevel(logging.DEBUG)

# --- This is the logger for CLI, we do not need it for now.
# ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
# ---

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

# --- This is the logger for CLI, we do not need it for now.
# ch.setFormatter(formatter)
# logger.addHandler(ch)
# ---

logger.info("Tutle Wallet Stated")
signal.signal(signal.SIGINT, signal.SIG_DFL) # Required to handle interrupts closing the program
logger.info("Starting Splash Screen")
splash_screen = SplashScreen() # Create a new instance of the splash screen

# Make sure the splash screen wasn't cancelled by the user
if not splash_screen.startup_cancelled:
    Gtk.main() # Start the main GTK loop
else:
    logger.info("Tutle Wallet exiting")

if global_variables.wallet_connection:
    logger.info("Stopping wallet daemon")
    global_variables.wallet_connection.stop_wallet_daemon()
