#!/usr/bin/env python3.7
import time
import argparse
import logging
import os
from IPoFB.pipeline.gateways import FacebookGatewayBlock
from IPoFB.pipeline.encoders import Base64Encoder
from IPoFB.pipeline.buffers import FileBinaryBuffer
from IPoFB.pipeline.pipeline import Pipeline


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

    pipeline = Pipeline()
    pipeline.append_block(FileBinaryBuffer(args.file))
    pipeline.append_block(Base64Encoder())
    pipeline.append_block(FacebookGatewayBlock(email, password))

    if args.mode == "send":
        logging.info(f"Sending file {args.file}")
        # Sends file
        pipeline.send()
    else:
        logging.info(f"Receiving file {args.file}")
        start_time = time.time()
        # Downloads to file
        pipeline.recv()
        elapsed_time = time.time() - start_time
        logging.info(f"Downloaded {os.stat(args.file).st_size} bytes in "
                     f"{elapsed_time} seconds")


if __name__ == "__main__":
    main()
