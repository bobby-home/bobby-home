# Docker network
## Create your network's
Please run the `docker-network.sh` script to create networks.
You could, eventually, get this kind of error: `ERROR: Pool overlaps with other one on this address space`. That means that, you have another docker network that overlaps with the specified address space in the script.

First of all, please make sure that you don't need the another network, this is your responsability, you could break other apps... If you need this address space, just change it on the script `docker-network.sh` and in Compose file. But be aware that you'll have also to change IP addresses for IoT devices, as they don't use Docker so they can't use service resolution name.

If you're sure that you don't need the existing network, you can delete it. **Even if the containers are down the networks are still persist. With no container running docker network prune did it.**.

```
docker network prune
```
Will clean your networks.

### MQTT
Make sure that you have the subnetwork `172.19.0.0/16` available. The MQTT broker has to have static IP, so my devices, arduino, esp... can connect to it statically, no DNS needed it's way too heavy.


The IP of the mqtt broker will be `172.19.0.3` by default.

## Compose network
The django API and PostgreSQL database are accessible on the `webapp_backend` network.
If you need to join the API with some services, you have to "join" this network.

Thank to this, you can request the api with `http://web:8000`. Django settings allows the domain `web` which is the name of the service.

More information: [docker compose networking](https://docs.docker.com/compose/networking/).

# Docker Utils

Migrate the database.
```
docker-compose exec web pipenv run python manage.py migrate --noinput
```

Create super user.
```
docker-compose exec web pipenv run python manage.py createsuperuser
```

Connect to the database.

```
docker-compose exec database psql -U hello_django -d hello_django_dev
# and then, list tables ect...
\dt
```

## To read for the database
:warning: Some initialization things are only run if you start the container with a data directory that is empty; any pre-existing database will be left untouched on container startup. In this case, you will see this message at the beginning. Source: [psql docker image documentation](https://hub.docker.com/_/postgres).

```
PostgreSQL Database directory appears to contain a database; Skipping initialization
```
For instance, this is the case for the database creation if you specifies the env variable `POSTGRES_DB`.
If you want to reset the database during development phase because you messsed up:

```
docker container rm <container>
docker volume rm <container>
```
Then, you can up the service with docker-compose, it will automatically create a fresh volume for you and you're good to go, the database is beeing initialized:
```
Creating volume "webapp_psql-data" with local driver
...
```

Create new django application.
```
docker-compose exec web pipenv run python manage.py startapp <application_name>

# as docker is sudo... We have to change the owner
sudo chown -R $USER:$USER ./app/<application_name>
```

# MQTT Broker
I'm using the MQTT protocol to connect my different devices. I've made the choice to use Mosquitto MQTT Broker running on my raspberryPI,
but why? I could have use something like Amazon IoT. Let's see that!

# Why local MQTT Broker?
Using a local MQTT Broker is a little bit painful, at least compared to using something in the cloud plug & play. For example, you have to manage your certificates to have TLS and so one.
You also have to ensure a good availability because this service is the root of everything. Every IoT device will communicate through it.
No more MQTT Broker? No more home security!

## Reach the outside world
The system was designed in the first place to be installed in a small countryside in France, so internet problems happen. I have to ensure that the system works without outside internet.
If the system can't reach the outside world, at least everything's locally have to work, if someone breaks in the house, the alarm should be triggered.

## Availability issues
So yeah, I won't use any cloud service provider to support my MQTT Broker, so I will have to manage myself the service availability.
To do this, I will monitor this service very closely and have alerts if something's goes wrong.
*Because yes, you can do everything, something wrong will still happens at some time.*

# Security
First you must generate the certificates used for TLS, if you already have certificates skip to the next section.
