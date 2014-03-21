#!/usr/bin/env bash

function usage() {
    echo "usage: route_to_za [enable|disable]"
    exit
}

[[ $# != 1 ]] && usage 

case $1 in
    enable)   sudo route add -host za gw myserver ;;
    disable)  sudo route del za ;;
    *)        usage ;;
esac

