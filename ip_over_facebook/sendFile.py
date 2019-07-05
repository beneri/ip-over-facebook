#!/usr/bin/env python3.7
import time
import argparse
import logging
from ip_over_facebook.facebook import Facebook


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
        if args.mode == "server":
            logging.info("Acting server, connecting to facebook")
            with open(args.file, 'rb') as data:
                fb.send(data.read())
        else:
            logging.info("Acting client, connecting to facebook")
            with open(args.file, 'wb') as f:
                start_time = time.time()
                data = fb.recv()
                elapsed_time = time.time() - start_time
                logging.info(f"Downloaded {len(data)} bytes in "
                             f"{elapsed_time} seconds")

                f.write(data)


if __name__ == "__main__":
    main()
