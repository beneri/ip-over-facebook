# IP over Facebook
Does your ISP give you free access to Facebook? Do you have access to Facebook but not other services (Due to Internet.org, firewalls, etc)? Then Facebook.py might be the tool for you! 

facebook.py provides simple APIs for sending any type of data over Facebook.
The send and receive functions updates and reads the "About You" field on Facebook.
The main reason for using this field is that it is not rate-limited, in contrast to Messenger, and allows for big messages, up to 1 MB. 

# tun.py 
tun.py demonstrates that both IP and TCP packets can be tunnelled over facebook. 
While possible, it is quite slow and using TCP results in a lot of packet retransmissions. 

## Usage
On the client: python tun.py client
On the server: python tun.py server
This will allow data to be sent from the client (192.168.7.1) to the server (192.168.7.2). 

# sendFile.py
While IP and TCP are not optimal, sending bigger files directly can actually be accomplished with feasible throughput. 
sendFile.py sends a full file by base64 encoding it and splitting it up into chunks, which are then transmitted. Furthermore, the chunks can be decoded independently, allowing for streaming of files. 

## Usage
On the client: python sendFile.py client video_in.mp4
On the server: python sendFile.py server video.mp4
The server will read the file video.mp4 and send it. The client will store the received data in video_in.mp4.

# Note
The data being sent is only encoded, not encrypted, meaning Facebook could read it. 






