## Related issues
- 73 to build the OpenCV image for multiple architecture (amd64 / armv7)

## Build the OpenCV docker image
```bash
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes && \
sudo systemctl restart docker && \
docker buildx build --push --platform linux/arm/v7,linux/amd64 --tag mxmaxime/rpi4-opencv:latest .
```

## Python version
When I used Python 3.8.x, I got this python error:
```
TypeError: item 9 in _argtypes_ passes a union by value, which is unsupported
```

I found the solution: I had to downgrade to Python 3.7.4.

Source: https://stackoverflow.com/questions/59892863/python-error-typeerror-item-1-in-argtypes-passes-a-union-by-value-which-is


## PyGame
When I was installing PyGame on my RPI, I got this error:
```
Hunting dependencies...
sh: 1: sdl-config: not found
sh: 1: sdl-config: not found
sh: 1: sdl-config: not found
WARNING: "sdl-config" failed!
```

Then, I researched the package:
```
sudo apt install apt-file
apt-file search "sdl-config"
```

Which gave me:
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
