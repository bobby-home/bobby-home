# Raspberrypi central
This is the raspberrypi (or other similar device), that will orchestrate a lot of things, this is the heart of the system.

## Setup connexion

### SSH Keys
I suggest you (strongly recommend), to activate SSH connexion with ssh keys.
That can be done easily by the `keys.sh` script that will:
- generate a key pair (ed25519)
- send them on the rpi by ssh login@pi (you'll be asked the login & pi).
- create your ~/.ssh/config for you if you want to, so you can easily connect to your rpi by doing `ssh user@hostname`. The hostname will be asked.

This script is not bullet proof, this is my simple use case, how I create my keys. Simple but effective.

Note that I also use this script to setup ssh on my servers on my day to day basis.
