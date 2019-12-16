#!/usr/bin/env bash

JSONSH_SEPARATOR="\t:\t"

CURRENT_DATE=`date`

HERE=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

JSONSH_DIR=${HERE}/libs/
source ${HERE}/contrib/jsonsh-lib.sh || exit 1

parseArguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
        --data)
            shift
            POST_DATA=$1
            ;;
        --domain)
            shift
            DOMAIN=$1
            ;;
        --sub-domain)
            shift
            SUB_DOMAIN=$1
            ;;
        --ip)
            shift
            IP=$1
            ;;
        *)
            echo "Unknow parameter $1"
            exit 0
            ;;
        esac
        shift
    done
}

main()
{
    parseArguments "$@"

    if [ -z "$DOMAIN" ]; then
        echo "--domain please!"
        exit 0
    fi

    if [ -z "$IP" ]; then
        $IP = $(dig @resolver1.opendns.com ANY myip.opendns.com +short)
    fi

    read status content < <(./ovh-api-bash-client.sh --method GET --url "/domain/zone/${DOMAIN}/dynHost/record")

    loadJSON "${content}"
    read id < <(getJSONValue 0)

    read status content < <(./ovh-api-bash-client.sh --method GET --url "/domain/zone/maxime-moreau.fr/dynHost/record/$id")
    # echo $content

    loadJSON "${content}"
    read current_ip < <(getJSONValue ip)

    if [ "$current_ip" != "$IP" ]; then
        echo "[$CURRENT_DATE] update ip from $current_ip to $IP"
        read status content < <(./ovh-api-bash-client.sh --method PUT --url "/domain/zone/${DOMAIN}/dynHost/record/${id}" --data '{"ip": "'$IP'", "subDomain": "'$SUB_DOMAIN'"}')
    else
        echo "[$CURRENT_DATE] no change"
        exit 0
    fi
    # echo $status $content
}

main "$@"

exit 0
