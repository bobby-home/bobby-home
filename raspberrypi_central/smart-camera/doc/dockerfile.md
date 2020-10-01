## Access the PI cam from container
Erreur sur l'accès à la caméra du rpi dans un container:

```
mmal: mmal_vc_shm_init: could not initialize vc shared memory service
mmal: mmal_vc_component_create: failed to initialise shm for 'vc.camera_info' (7:EIO)
mmal: mmal_component_create_core: could not create component 'vc.camera_info' (7)
mmal: Failed to create camera_info component
```
Résolu grâce au flag `privileged: true` et la politique d'accès à la camera.
See: https://www.losant.com/blog/how-to-access-the-raspberry-pi-camera-in-docker
