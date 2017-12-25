#!/usr/bin/env bash

# Template: OpenBazaar
#
# install_dependencies.sh - Setup dependencies for compiling TurtleCoin and TurtleWallet
#
# Credits: Forknote
#
# Code borrowed from:
# https://github.com/forknote/
# https://github.com/OpenBazaar/OpenBazaar/blob/develop/configure.sh
# https://github.com/Quanttek/install_monero/blob/master/install_monero.sh

#exit on error
set -e

function command_exists {
  # this should be a very portable way of checking if something is on the path
  # usage: "if command_exists foo; then echo it exists; fi"
  type "$1" &> /dev/null
}

function unsupportedOS {
	echo "Unsupported OS. Only Ubuntu 16 is supported right now."
}

function installUbuntu {
  . /etc/lsb-release

  # print commands
  set -x

  if [[ $DISTRIB_ID=Ubuntu && $DISTRIB_RELEASE == 16.04 ]] ; then
    sudo apt-get update
    sudo apt-get -y install python-gi python-gi-cairo python3-gi python3-gi-cairo gir1.2-gtk-3.0 build-essential python-dev python-pip gcc-4.9 g++-4.9 git cmake libboost1.58-all-dev librocksdb-dev
    sudo pip install psutil
    sudo pip install requests
    sudo pip install tzlocal
    export CXXFLAGS="-std=gnu++11"

    doneMessage
  elif [[ $DISTRIB_ID=Ubuntu && $DISTRIB_RELEASE == 16.10 ]] ; then
    sudo apt-get update
    sudo apt-get -y install python-gi python-gi-cairo python3-gi python3-gi-cairo gir1.2-gtk-3.0 build-essential python-dev python-pip gcc-4.9 g++-4.9 git cmake libboost1.61-all-dev librocksdb-dev
    sudo pip install psutil
    sudo pip install requests
    sudo pip install tzlocal
    export CXXFLAGS="-std=gnu++11"

    doneMessage
  else
    echo "Only Ubuntu 16 is supported"
  fi
}

function doneMessage {
  echo "TurtleCoin configuration finished."
}

if [[ $OSTYPE == darwin* ]] ; then
	  unsupportedOS
elif [[ $OSTYPE == linux-gnu || $OSTYPE == linux-gnueabihf ]]; then
    installUbuntu
else
	  unsupportedOS
fi
