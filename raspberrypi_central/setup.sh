#!/bin/bash

# parameters to handle: "host@distantMachine" and root password
#
#
#

# if you need password for sudo.
#ssh "$1" 'echo "$2" | sudo -Sv && bash -s' < install.sh

ssh "$1" 'bash -s' < install.sh
