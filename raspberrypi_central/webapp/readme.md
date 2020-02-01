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

tK_OG3TF9wKRipWPMaOkArlJ1F_ahMXYCgl2dm_IGSYYhAo_37yHpVVvznBpMrcbp5dRPB1pmbug7mL0o299BQ
