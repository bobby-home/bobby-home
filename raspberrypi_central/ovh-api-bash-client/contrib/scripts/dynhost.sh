#!/usr/bin/env bash
HERE=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
source ${HERE}/../ovh-api-lib.sh || exit 1

JSONSH_SEPARATOR="\t:\t"
CURRENT_DATE=`date`

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
        IP=`dig @resolver1.opendns.com -4 myip.opendns.com +short`
    fi

    DNS_CURRENT_IP=`dig +short $SUB_DOMAIN.$DOMAIN`

    if [ "$DNS_CURRENT_IP" != "$IP" ]; then
        # get the "id" record. Please not that we take the first Dynhost here /!\
        # read status content < <(./ovh-api-bash-client.sh --method GET --url "/domain/zone/${DOMAIN}/dynHost/record")
        # loadJSON "${content}"
        OvhRequestApi "/domain/zone/${DOMAIN}/dynHost/record"
        read id < <(getJSONValue 0)

        # echo "working on $id dns record (id)"

        OvhRequestApi "/domain/zone/${DOMAIN}/dynHost/record/${id}" "PUT" '{"ip": "'$IP'", "subDomain": "'$SUB_DOMAIN'"}'
        if [ "${OVHAPI_HTTP_STATUS}" -eq 200 ]; then
            echo "[$CURRENT_DATE] success: update ip from '$DNS_CURRENT_IP' to '$IP'"
        else
            echo "[$CURRENT_DATE] error: ovh api call failed"
        fi

        # read status content < <(./ovh-api-bash-client.sh --method PUT --url "/domain/zone/${DOMAIN}/dynHost/record/${id}" --data '{"ip": "'$IP'", "subDomain": "'$SUB_DOMAIN'"}')
    else
        echo "[$CURRENT_DATE] success: no change $IP"
        exit 0
    fi
}

# OvhRequestApi /me

# if [ ${OVHAPI_HTTP_STATUS} -ne 200 ]; then
#   echo "profile error:"
#   getJSONValues
#   exit
# fi

# OvhRequestApi "/domain"

# if [ "${OVHAPI_HTTP_STATUS}" -eq 200 ]; then
#    domains=($(getJSONValues))
#    echo "number of domains=${#domains[@]}"

#    # for example, only list for first domain
#    #for domain in "${domains[@]}"
#    for domain in "${domains[0]}"
#    do
#      echo -e "\n== informations about ${domain} =="
#      OvhRequestApi "/domain/${domain}"
#      echo "-- single value --"
#      # key can be passed with/without double quote
#      getJSONValue lastUpdate
#      getJSONValue '"transferLockStatus"'
#      echo "-- get all values --"
#      getJSONValues
#    done
# else
#   getJSONValues
# fi

main "$@"
