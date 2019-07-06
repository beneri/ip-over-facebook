#!/usr/bin/env python3.7
import time
import argparse
import logging
from IPoFB.gateways.facebook import Facebook


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', help='server or client')
    parser.add_argument('file', help='file to send (sever) or save (client)')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    (email, password) = open("creds.txt").read().split()
    fb = Facebook("cache")
    login_ok = fb.login(email, password)

    if login_ok:
        if args.mode == "send":
            logging.info(f"Sending file {args.file}")
            with open(args.file, 'rb') as data:
                fb.send(data.read())
        else:
            logging.info(f"Receiving file {args.file}")
            with open(args.file, 'wb') as f:
                start_time = time.time()
                for data_chunk in fb.recv():
                    f.write(data_chunk)
                elapsed_time = time.time() - start_time
                logging.info(f"Downloaded {len(data)} bytes in "
                             f"{elapsed_time} seconds")


if __name__ == "__main__":
    main()
