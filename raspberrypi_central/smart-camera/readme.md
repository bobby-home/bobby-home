Lors de l'installation de pygame sur rpi, j'avais cette erreur:
```
Hunting dependencies...
sh: 1: sdl-config: not found
sh: 1: sdl-config: not found
sh: 1: sdl-config: not found
WARNING: "sdl-config" failed!
```

Recherche du package:
```
sudo apt install apt-file
apt-file search "sdl-config"
```

Qui me donne:
```
emscripten: /usr/share/emscripten/system/bin/sdl-config
libsdl1.2-dev: /usr/bin/sdl-config
libsdl1.2-dev: /usr/share/man/man1/sdl-config.1.gz
lush-library: /usr/share/lush/packages/sdl/sdl-config.lsh
```

I'm searching for a binary, so I'm downloading this package:
```
sudo apt install libsdl1.2-dev
```

Erreur sur l'accès à la caméra du rpi dans un container:

```
mmal: mmal_vc_shm_init: could not initialize vc shared memory service
mmal: mmal_vc_component_create: failed to initialise shm for 'vc.camera_info' (7:EIO)
mmal: mmal_component_create_core: could not create component 'vc.camera_info' (7)
mmal: Failed to create camera_info component
```
Résolu grâce au flag `privileged: true` et la politique d'accès à la camera.
See: https://www.losant.com/blog/how-to-access-the-raspberry-pi-camera-in-docker

Autre erreur:
```
TypeError: item 9 in _argtypes_ passes a union by value, which is unsupported
```

J'étais sur Python 3.8.x, il s'avère qu'il fallait downgrade sur python 3.7.4

Source:https://stackoverflow.com/questions/59892863/python-error-typeerror-item-1-in-argtypes-passes-a-union-by-value-which-is
