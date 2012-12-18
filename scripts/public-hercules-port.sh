#!/usr/bin/env bash

usage() {
    echo "usage:"
    echo "  public-hercules-port <enable|disable>"
}

[[ $# != 1 ]] && usage && exit

case $1 in
    enable)
        sudo iptables -D INPUT -s 127.0.0.1 -j ACCEPT
        sudo iptables -D INPUT -p tcp --dport 3270 -j REJECT
        sudo iptables -D INPUT -p udp --dport 3270 -j REJECT
        ;;
    disable)
        sudo iptables -A INPUT -s 127.0.0.1 -j ACCEPT
        sudo iptables -A INPUT -p tcp --dport 3270 -j REJECT
        sudo iptables -A INPUT -p udp --dport 3270 -j REJECT
        ;;
    *) 
        usage
        ;;
esac

