## The choice of the base image.
Some day I've tried naively to use the alpine based image and I got some troubles. For instance, the package `psycopg2-binary` don't work out of the box this alpine image. [Please see this issue explaining why.](https://github.com/psycopg/psycopg2/issues/684)


To read: https://pythonspeed.com/articles/base-image-python-docker-images/
