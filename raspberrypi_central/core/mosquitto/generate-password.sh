# -c = user
user=$1

DEST_FOLDER="$PWD/../config/mosquitto"

if [ -z "$user" ]; then
    echo "Must provide user parameter"
    exit 1
fi

echo "Generate mqtt '$user' user"

docker run -it --rm -v $DEST_FOLDER:/mosquitto/config eclipse-mosquitto mosquitto_passwd -c /mosquitto/config/passwd $user
