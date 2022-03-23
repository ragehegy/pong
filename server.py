import socket
from _thread import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = 'localhost'
port = 5555

server_ip = socket.gethostbyname(server)

current_players = 0

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(4)
print("Waiting for a connection")

total_players = 0

pos = ["0:490,235", "1:0,235", "2:235,490", "3:235,0"]

def threaded_client(conn):
    global total_players, pos
    if total_players > 4:
        reply = "False"
    else:
        conn.send(str.encode(pos[total_players]))
        total_players += 1
        reply = ''
        while True:
            try:
                data = conn.recv(2048)
                reply = data.decode('utf-8')
                if not data:
                    conn.send(str.encode("Goodbye"))
                    break
                else:
                    # print("Recieved: " + reply)
                    arr = reply.split(":")
                    id = int(arr[0])
                    pos[id] = reply
                    # print("pos: ", pos)

                    new_pos = [x for i, x in enumerate(pos) if i != id]
                    reply = "-".join(new_pos)

                # print("Sending: " + reply)
                conn.sendall(str.encode(reply))
            except:
                break

        print("Connection Closed")
        total_players -= 1
        conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))