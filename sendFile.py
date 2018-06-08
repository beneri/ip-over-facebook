import time
import argparse
from facebook import Facebook



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('mode', help='server or client')
    parser.add_argument('file', help='file to send (sever) or save (client)')
    args = parser.parse_args()


    (email,password) = file("creds.txt").read().split()
    fb = Facebook("cache.txt")
    login_ok = fb.login(email, password)

    if login_ok:
        if( args.mode == "server" ):
            print "Acting server, connecting to facebook"
            data = file(args.file,'rb').read()
            fb.send(data)
        else:
            print "Acting client, connecting to facebook"
            f = open(args.file, 'w')
            start_time = time.time()
            data = fb.recv()
            elapsed_time = time.time() - start_time
            print "Downloaded", len(data), "bytes in ", elapsed_time, "seconds"

            f.write(data)
            f.close()


