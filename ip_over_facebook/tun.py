#!/usr/bin/env python3
import subprocess
import argparse
import logging
from pytun import TunTapDevice
from ip_over_facebook.facebook import Facebook


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', help='server or client')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-c', '--client-ip', default="10.8.0.1")
    parser.add_argument('-s', '--server-ip', default="10.8.0.2")
    parser.add_argument('-n', '--interface-name', default="IPoFB")
    parser.add_argument('-m', '--mtu', default=1500)
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    # Log in to facebook
    email, password = open("creds.txt").read().split()
    fb = Facebook("cache")
    login_ok = fb.login(email, password)

    if not login_ok:
        logging.error("login failed, exit")
        exit(1)

    tun = TunTapDevice(name=args.interface_name)
    tun.addr = args.client_ip
    tun.dstaddr = args.server_ip
    tun.netmask = '255.255.255.0'
    tun.mtu = args.mtu

    tun.up()

    # Bring it up and assign addresses.
    if args.mode == 'client':
        subprocess.check_call(f'ifconfig {tun.name} {args.client_ip} '
                              f'pointopoint {args.server_ip} up',
                              shell=True)
    else:
        subprocess.check_call(f'ifconfig {tun.name} {args.server_ip} '
                              f'pointopoint {args.client_ip} up',
                              shell=True)

    while True:
        packet = tun.read(tun.mtu)
        logging.debug(f"Sending {packet} to facebook")
        if packet:
            fb.send(packet)

        packet = fb.recv()
        logging.debug(f"Received {packet} from facebook")
        if packet:
            tun.write(packet)

    tun.down()


if __name__ == "__main__":
    main()
