# Docker network
The django API and PostgreSQL database are accessible on the `webapp_backend` network.
If you need to join the API with some services, you have to "join" this network. Ex with `docker-compose`:

```yml
# at the end of your docker-compose.yml
networks:
    default:
        external: 
            name: webapp_webapp_backend
```

Thank to this, you can request the api with `http://web:8000`. Django settings allows the domain `web` which is the name of the service.

More information: [docker compose networking](https://docs.docker.com/compose/networking/).

## Utils

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

Create new django application.
```
docker-compose exec web pipenv run python manage.py startapp <application_name>

# as docker is sudo... We have to change the owner
sudo chown -R $USER:$USER ./app/<application_name>
```

tK_OG3TF9wKRipWPMaOkArlJ1F_ahMXYCgl2dm_IGSYYhAo_37yHpVVvznBpMrcbp5dRPB1pmbug7mL0o299BQ
