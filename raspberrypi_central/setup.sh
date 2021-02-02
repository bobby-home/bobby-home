#!/bin/bash

# parameters to handle: "host@distantMachine" and root password
#
#
#

#ssh "$1" 'echo "$2" | sudo -Sv && bash -s' < install.sh

ssh "$1" 'bash -s' < install.sh
