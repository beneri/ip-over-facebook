#!/usr/bin/env python3

import fcntl
import os
import struct
import subprocess
import argparse
import logging
from facebook import Facebook


# Some constants used to ioctl the device file. I got them by a simple C
# program.
TUNSETIFF = 0x400454ca
TUNSETOWNER = TUNSETIFF + 2
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', help='server or client')
    parser.add_argument('-d', '--debug', actions='store_true')
    parser.add_argument('-c', '--client-ip', default="localhost")
    parser.add_argument('-s', '--server-ip', default="localhost")
    args = parser.parse_args()

    # Open file corresponding to the TUN device.
    tun = open('/dev/net/tun', 'r+b')
    ifr = struct.pack('16sH', 'tun0', IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    fcntl.ioctl(tun, TUNSETOWNER, 1000)

    # Log in to facebook
    email, password = open("creds.txt").read().split()
    fb = Facebook("cache.txt")
    login_ok = fb.login(email, password)

    if not login_ok:
        logging.error("login failed, exit")
        exit(1)

    # Bring it up and assign addresses.
    if args.mode == 'client':
        subprocess.check_call(f'ifconfig tun0 {args.client_ip} '
                              f'pointopoint {args.server_ip} up',
                              shell=True)
    else:
        subprocess.check_call('ifconfig tun0 {args.server_ip} '
                              f'pointopoint {args.client_ip} up',
                              shell=True)

    while True:

        if args.mode == 'client':
            logging.debug("Waiting for packet on interface")
            # Read an IP packet been sent to this TUN device.
            packet = list(os.read(tun.fileno(), 2048))
            to_ip = str(ord(packet[16])) + "." + str(ord(packet[17])) + "." \
                + str(ord(packet[18])) + "." + str(ord(packet[19]))

            if to_ip == args.server_ip:
                logging.debug("Correct ip, sending!")
                logging.debug(f"Got: {packet}")

                logging.debug(f"TO {to_ip}")
                logging.debug(f"Send to remote fb: {packet}")
                fb.send(''.join(packet))

                logging.debug("Waiting for answer")
                data = fb.recv()

                # Write the reply packet into TUN device.
                # os.write(tun.fileno(), ''.join(packet))
                os.write(tun.fileno(), data)
                logging.debug("Sent: {packet}")
            else:
                logging.debug("Packet to {to_ip} was ignored")
        else:
            logging.debug("Waiting for fb")
            data = fb.recv()

            logging.debug(f"Got: {list(data)} from fb")
            os.write(tun.fileno(), data)

            logging.debug("waiting for OS answer")
            packet = list(os.read(tun.fileno(), 2048))

            logging.debug("sending OS answer")
            fb.send(''.join(packet))
