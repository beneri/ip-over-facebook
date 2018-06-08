import fcntl
import os
import struct
import subprocess
import sys
from facebook import Facebook


client_ip = "192.168.7.1"
server_ip = "192.168.7.2"

# Some constants used to ioctl the device file. I got them by a simple C
# program.
TUNSETIFF = 0x400454ca
TUNSETOWNER = TUNSETIFF + 2
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000

# Open file corresponding to the TUN device.
tun = open('/dev/net/tun', 'r+b')
ifr = struct.pack('16sH', 'tun0', IFF_TUN | IFF_NO_PI)
fcntl.ioctl(tun, TUNSETIFF, ifr)
fcntl.ioctl(tun, TUNSETOWNER, 1000)

if not (len(sys.argv) == 2 and (sys.argv[1] == 'client'
                             or sys.argv[1] == 'server')):
    print "Use: python linux_client.py [client|server]"
    exit()

# Log in to facebook
(email,password) = file("creds.txt").read().split()
fb = Facebook("cache.txt")
login_ok = fb.login(email, password)

if not login_ok:
    print "login failed, exit"
    exit(1)

mode = sys.argv[1]
# Bring it up and assign addresses.
if( mode == 'client' ):
    subprocess.check_call('ifconfig tun0 '+client_ip+' pointopoint '+server_ip+' up',
        shell=True)
else:
    subprocess.check_call('ifconfig tun0 '+server_ip+' pointopoint '+client_ip+' up',
        shell=True)

while True:

    if( mode == 'client'  ):
        print "Waiting for packet on interface"
        # Read an IP packet been sent to this TUN device.
        packet = list(os.read(tun.fileno(), 2048))
        to_ip = str(ord(packet[16])) + "." + str(ord(packet[17])) + "." + str(ord(packet[18])) + "." + str(ord(packet[19]))

        if( to_ip == server_ip ):
            print "Correct ip, sending!"
            print "Got: ", packet

            print "TO ", to_ip
            print "Send to remote fb: ", packet
            fb.send(''.join(packet))

            print "Waiting for answer"
            data = fb.recv()

            # Write the reply packet into TUN device.
            #os.write(tun.fileno(), ''.join(packet))
            os.write(tun.fileno(), data)
            print "Sent: ", packet
        else:
            print "Packet to ", to_ip, " was ignored"
    else:
        print "Waiting for fb"
        data = fb.recv()

        print "Got: ", list(data), " from fb"
        os.write(tun.fileno(), data)

        print "waiting for OS answer"
        packet = list(os.read(tun.fileno(), 2048))

        print "sending OS answer"
        fb.send(''.join(packet))
