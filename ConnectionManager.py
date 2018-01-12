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
        walletd_filename = "walletd" if os.name != 'nt' else "walletd.exe"
        walletd_exec = os.path.join(os.getenv('TURTLE_HOME', '.'), walletd_filename)
        if not os.path.isfile(walletd_exec):
            raise ValueError("Cannot find wallet at location: {}".format(walletd_exec))

        return walletd_exec

    def stop_wallet_daemon(self):
        if self.walletd:
            self.walletd.terminate()
            # Let's loop until walletd no longer is running, we'll give it 3 strikes.
            time_to_kill = 0
            while self.walletd.poll() is None:
                time_to_kill += 1
                time.sleep(1)
                print("Waiting on walletd to terminate...")
                if time_to_kill == 3:
                    self.walletd.kill()
                    print("FATALITY!")

    def __init__(self, wallet_file, password):
        self.rpc_connection = RPCConnection("http://127.0.0.1:8070/json_rpc")
        if not os.path.isfile(wallet_file):
            raise ValueError("Cannot find wallet file at: {}".format(wallet_file))
        self.walletd = Popen([self.get_wallet_daemon_path(),
                              '-w', wallet_file,
                              '-p', password,
                              '--local'])

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

        try:
            # Make the request to the endpoint with specified data
            response = requests.post(self.url, data=json.dumps(payload), headers=self.headers).json()

            # Check if the response returned an error, and extract and wrap it in an exception if it has
            if 'error' in response:
                print("Failed to talk to server: %s" % (response,))
                #raise Exception("Connection to Walletd RPC failed with error: {0} {1}".format(response['error']['code'], response['error']['message']))
            else:
                print("RESPONSE: %s" % response)
            return response
        except ConnectionError as e:
            raise ValueError("Failed to talk to wallet daemon!")


def open_wallet():
    """Opens the wallet, this should only be run off the main thread."""
    wallet = None
    try:
        wallet = WalletConnection()
        while True:
            # Check if walletd is actually running
            if not wallet.walletd.poll():
                response = wallet.request("getStatus")
                if 'error' in response:
                    print("Still waiting for daemon response...")
                    time.sleep(2)
                else:
                    break
            else:
                print("Waiting for the daemon to start...")
                time.sleep(2)
    except Exception as e:
        print("Unable to establish connection to wallet, is walletd running?")
        print("%s" % e)
    return wallet
