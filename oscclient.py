from pythonosc.udp_client import SimpleUDPClient

ip = ''
port = ''
client = None

def init(addr, p):
    global ip, port, client
    ip = addr
    port = p
    client = SimpleUDPClient(ip, int(port))  # Create client

def sendOSC(command):
    global client
    try:
        client.send_message(command, 0)   # Send float message
    except OSError:
        print('OSC not configured!')
        pass