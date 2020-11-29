## Access the PI cam from container
I got this error when I was trying to access to the PI camera:

```
mmal: mmal_vc_shm_init: could not initialize vc shared memory service
mmal: mmal_vc_component_create: failed to initialise shm for 'vc.camera_info' (7:EIO)
mmal: mmal_component_create_core: could not create component 'vc.camera_info' (7)
mmal: Failed to create camera_info component
```

I fixed this issue by adding the flag `privileged: true` in the compose file.
See: https://www.losant.com/blog/how-to-access-the-raspberry-pi-camera-in-docker
