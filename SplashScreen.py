# -*- coding: utf-8 -*-
""" SplashScreen.py

This file represents the splash screen window, and the underlying
logic required for it. It loads the corresponding Glade file, of
the same name.
"""

import threading
import time
from gi.repository import Gtk, GLib
from __init__ import __version__
from ConnectionManager import WalletConnection
import global_variables
from requests import ConnectionError
from MainWindow import MainWindow
import logging


# Maximum attempts to talk to the wallet daemon before giving up
MAX_FAIL_COUNT = 15

# Get Logger made in start.py
splash_logger = logging.getLogger('trtl_log.splash')

class SplashScreen(object):
    """
    This class is used to interact with the SplashScreen glade file
    """
    def on_SplashScreenWindow_delete_event(self, object, data=None):
        """Called by GTK when the user requests the window be closed"""
        Gtk.main_quit() # Quit the GTK main loop to exit

    def update_status(self, message):
        """Updates the status label with a new message"""
        self.status_label.set_label(message) # Set the label text

    def open_main_window(self):
        """Opens the main window, closing the splash window"""
        main_window = MainWindow() # Initialise the main window
        self.window.destroy() # Destroy the splash screen window

    def initialise(self, wallet_file, wallet_password):
        """Initialises the connection to the wallet
            Note: Wallet must already be running at this point"""

        # There will be an exception if there is a failure to connect at any point
        # TODO: Handle exceptions gracefully

        time.sleep(1)
        GLib.idle_add(self.update_status, "Connecting to walletd")
        splash_logger.info("Connecting to walletd, entering wait loop")
        # Initialise the wallet connection
        # If we fail to talk to the server so many times, it's hopeless
        fail_count = 0
        try:
            global_variables.wallet_connection = WalletConnection(wallet_file, wallet_password)
            # Loop until the block count is greater than or equal to the known block count.
            # This should guarantee us that the daemon is running and synchronized before the main
            # window opens.
            while True:
                time.sleep(1.5)
                try:
                    # In the case that the daemon started but stopped, usually do to an
                    # invalid password.
                    if not global_variables.wallet_connection.check_daemon_running():
                        splash_logger.error("Wallet daemon exited.")
                        raise ValueError("Wallet daemon exited.")
                    resp = global_variables.wallet_connection.request('getStatus')
                    block_count = resp['blockCount']
                    known_block_count = resp['knownBlockCount']
                    
                    # It's possible the RPC server is running but the daemon hasn't received
                    # the known block count yet. We need to wait on that before comparing block height.
                    if known_block_count == 0:
                        GLib.idle_add(self.update_status, "Waiting on known block count...")
                        continue
                    GLib.idle_add(self.update_status, "Syncing... [{} / {}]".format(block_count, known_block_count))
                    splash_logger.debug("Syncing... [{} / {}]".format(block_count, known_block_count))
                    # Even though we check known block count, leaving it in there in case of weird edge cases
                    if (known_block_count > 0) and (block_count >= known_block_count):
                        GLib.idle_add(self.update_status, "Wallet is synced, opening...")
                        splash_logger.info("Wallet successfully synced, opening wallet")
                        break
                except ConnectionError as e:
                    fail_count += 1
                    print("ConnectionError while waiting for daemon to start: {}".format(e))
                    splash_logger.warn("ConnectionError while waiting for daemon to start: {}".format(e))
                    if fail_count >= MAX_FAIL_COUNT:
                        splash_logger.error("Can't communicate to daemon")
                        raise ValueError("Can't communicate to daemon")
        except ValueError as e:
            splash_logger.error("Failed to connect to walletd: {}".format(e))
            print("Failed to connect to walletd: {}".format(e))
            GLib.idle_add(self.update_status, "Failed: {}".format(e))
            time.sleep(3)
            GLib.idle_add(Gtk.main_quit)
        time.sleep(1)
        # Open the main window using glib
        GLib.idle_add(self.open_main_window)

    def prompt_wallet_dialog(self):
        """
        Prompt the user to select a wallet file.
        :return: The wallet filename or none if they chose to cancel
        """
        # Opens file dialog with Open and Cancel buttons, with action set to OPEN (as compared to SAVE).
        dialog = Gtk.FileChooserDialog("Please select your wallet", self.window,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
        filename = None
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        dialog.destroy()
        return filename

    def prompt_wallet_password(self):
        """
        Prompt the user for their wallet password
        :return: Returns the user text or none if they chose to cancel
        """
        dialog = Gtk.MessageDialog(self.window,
                                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                   Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.OK_CANCEL,
                                   "Please enter the wallet password:")

        dialog.set_title("Wallet Password")

        # Setup UI for entry box in the dialog
        dialog_box = dialog.get_content_area()
        userEntry = Gtk.Entry()
        userEntry.set_visibility(False)
        userEntry.set_invisible_char("*")
        userEntry.set_size_request(250, 0)
        # Trigger the dialog's response when a user hits ENTER on the text box.
        # The lamba here is a wrapper to get around the default arguments
        userEntry.connect("activate", lambda w: dialog.response(Gtk.ResponseType.OK))
        # Pack the back right to left, no expanding, no filling, 0 padding
        dialog_box.pack_end(userEntry, False, False, 0)

        dialog.show_all()
        # Runs dialog and waits for the response
        response = dialog.run()
        text = userEntry.get_text()
        dialog.destroy()
        if (response == Gtk.ResponseType.OK) and (text != ''):
            return text
        else:
            return None

    def __init__(self):

        # Flag used to determine if startup is cancelled
        # to prevent the main thread from running.
        self.startup_cancelled = False

        # Initialise the GTK builder and load the glade layout from the file
        self.builder = Gtk.Builder()
        self.builder.add_from_file("SplashScreen.glade")

        # Get the version label on the splash screen
        self.version_label = self.builder.get_object("TurtleWalletVersionLabel")

        # Set the version label to match the version of the package
        self.version_label.set_label(__version__)

        # Get the status label
        self.status_label = self.builder.get_object("StatusLabel")

        # Set the status label value to indicate the program is starting
        self.status_label.set_label("Starting...")

        # Use the methods defined in this class as signal handlers
        self.builder.connect_signals(self)

        # Get the window from the builder
        self.window = self.builder.get_object("SplashScreenWindow")

        # Set the window title to reflect the current version
        self.window.set_title("TurtleWallet v{0}".format(__version__))
        splash_logger.info("TurtleWallet v{0}".format(__version__))

        # TODO: Option to create or open a wallet
        wallet_file = self.prompt_wallet_dialog()
        if wallet_file:
            splash_logger.info("Using wallet: " + wallet_file) 
            wallet_password = self.prompt_wallet_password()
            if wallet_password:
                # Show the window
                self.window.show()

                # Start the wallet initialisation on a new thread
                thread = threading.Thread(target=self.initialise, args=(wallet_file, wallet_password))
                thread.start()
            else:
                splash_logger.info("Invalid password")
                self.startup_cancelled = True
        else:
            splash_logger.warn("No wallet found, given, or created")
            self.startup_cancelled = True
