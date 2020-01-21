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


