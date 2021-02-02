
echo "Process to create and register new ssh keys."
echo "please enter the key name: id_"

read name

echo "Remote host that will receive the ssh key:"
read REMOTE_HOST

echo "Username to connect to this host:"
read USERNAME

KEYNAME="id_$name"

ssh-keygen -t ed25519 -f ~/.ssh/$KEYNAME

eval "$(ssh-agent -s)" >> /dev/null
ssh-add ~/.ssh/$KEYNAME

ssh-copy-id -i ~/.ssh/$KEYNAME $USERNAME@$REMOTE_HOST

echo "success. Do you want to create a config file for this remote host? y/n"
read res

if [[ $res == "y" ]]; then
    echo "What hostname do you want? You will be able to ssh user@host instead of using the IP address."
    read HOST
    conf="Host $HOST \n\t HostName $REMOTE_HOST \n\t User $USERNAME \n\t IdentityFile ~/.ssh/$KEYNAME \n\t IdentitiesOnly yes"
    echo -e $conf >> ~/.ssh/config
    echo "~/.ssh/config file edited."
    echo "Use ssh $USERNAME@$HOST to connect. Happy ssh!"
else
    echo "Okay then. Happy ssh!"
fi
