HERE=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
SCRIPT=$HERE/dynhost.sh

(crontab -l ; echo "*/5 * * * * $SCRIPT --domain maxime-moreau.fr --sub-domain parents-home") | crontab -
