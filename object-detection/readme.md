## Build

```
mkdir build && cd build
cmake ..
make
```

## Limitations
The device id is extracted from the topic by a simple regex: `\w+$`.
So your device id should match this regex.
If it's a uuid for example, the behavior will be broken because the service will publish things with the last part of the uuid.

