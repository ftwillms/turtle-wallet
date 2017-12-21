# -*- coding: utf-8 -*-
""" ConnectionManager.py

This file represents the logic required for the RPC
connections, currently just to Walletd.
"""

import json
import psutil
import requests

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

    def __init__(self):
        for proc in psutil.process_iter(): # Search the running process list for walletd
            if proc.name() == "walletd":
                # Initialise the RPC connection
                self.rpc_connection = RPCConnection("http://127.0.0.1:8070/json_rpc")
                #Test the RPC connection
                self.rpc_connection.request("getStatus")
                return

        raise Exception("Walletd not running")

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
            raise Exception("Connection to Walletd RPC failed with error: {0} {1}".format(response['error']['code'], response['error']['message']))
        else:
            return response
