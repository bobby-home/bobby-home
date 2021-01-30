docker network create --gateway 172.19.0.1 --subnet 172.19.0.0/16 backend_mqtt
docker volume create --driver local --name camera_videos
