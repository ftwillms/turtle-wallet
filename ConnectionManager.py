# -*- coding: utf-8 -*-
""" ConnectionManager.py

This file represents the logic required for the RPC
connections, currently just to Walletd.
"""

import json
import psutil
import requests
from requests import ConnectionError

import time
import os
import os.path
from subprocess import Popen


class WalletConnection(object):
    """
    This class represents an RPC connection to Walletd
    """
    def request(self, method, params={}):
        """Makes an RPC request to Walletd"""
        if self.rpc_connection is not None: # Check to make sure that an RPC connection has been established
            response = self.rpc_connection.request(method, params) # Make the request
            return response['result'] # Return the response from the request
        else:
            raise Exception("No RPC connection has been established!")

    def get_wallet_daemon_path(self):
        """
        Tries to find where walletd exists. Looks for TURTLE_HOME env and falls
        back to looking at the current working directory.
        For Windows (nt), the extension .exe is appended.
        :return: path to the walletd executable
        """
        walletd_filename = "walletd" if os.name != 'nt' else "walletd.exe"
        walletd_exec = os.path.join(os.getenv('TURTLE_HOME', '.'), walletd_filename)
        if not os.path.isfile(walletd_exec):
            raise ValueError("Cannot find wallet at location: {}".format(walletd_exec))

        return walletd_exec

    def check_daemon_running(self):
        for proc in psutil.process_iter():  # Search the running process list for walletd
            if proc.name() == "walletd" or proc.name() == "walletd.exe":
                return proc
        return None

    def start_wallet_daemon(self, wallet_file, password):
        """
        Fires off the wallet daemon and releases control once the daemon
        has successfully been spun up.

        :param wallet_file: path to the wallet file
        :param password: password for the wallet
        :return: popen instance of the wallet daemon process
        """
        existing_daemon = self.check_daemon_running()
        if existing_daemon:
            print("Daemon is already running: pid {}".format(existing_daemon.pid))
            return
        walletd = Popen([self.get_wallet_daemon_path(),
                        '-w', wallet_file, '-p', password, '--local'])
        # Poll the daemon, if poll returns None the daemon is active.
        while walletd.poll():
            time.sleep(1)
        # So now that the daemon is active, the password maybe invalid or
        # the user is still running Turtled and the daemon might die.
        # This is an attempt to wait for that to process.
        # When the main window appears the request status will naturally fail if the daemon is not running.
        if not walletd.poll():
            return walletd
        else:
            raise ValueError("Unable to open wallet daemon.")

    def stop_wallet_daemon(self):
        """
        Attempts to terminate (SIGTERM) the wallet daemon.
        Using Popen.wait() this will hold until the daemon is successfully terminated.
        :return:
        """
        if self.walletd:
            r = self.request("save")
            self.walletd.terminate()
            self.walletd.wait()

    def __init__(self, wallet_file, password):
        if not os.path.isfile(wallet_file):
            raise ValueError("Cannot find wallet file at: {}".format(wallet_file))
        self.walletd = self.start_wallet_daemon(wallet_file, password)
        port = os.getenv('DAEMON_PORT', 8070)  # If a user is running their own daemon, they can configure the port
        self.rpc_connection = RPCConnection("http://127.0.0.1:{}/json_rpc".format(port))


class RPCConnection(object):
    """
    This class makes requests to a JSON RPC 2.0 endpoint
    """
    def __init__(self, url):
        self.url = url # Just take the URL at face value, assume user has validated
        self.headers = {'content-type':'application/json'} # Set the headers
        self.id = 0 # Set the ID, which will increase with each call

    def request(self, method, params={}):
        """Makes an RPC request to the endpoint the class was initialised with"""

        # Initialise the payload that is to be sent to the remote endpoint
        payload = {
            "jsonrpc" : "2.0", # Using JSON RPC 2.0
            "method" : method, # The user specified method
            "params" : params, # The user specified, or default params
            "id" : self.id # The next ID in sequence
        }

        self.id += 1 # Increment the ID by one ready for the next call

        # Make the request to the endpoint with specified data
        response = requests.post(self.url, data=json.dumps(payload), headers=self.headers).json()

        # Check if the response returned an error, and extract and wrap it in an exception if it has
        if 'error' in response:
            print("Failed to talk to server: %s" % (response,))
            raise ValueError("Walletd RPC failed with error: {0} {1}".format(response['error']['code'], response['error']['message']))
        return response
