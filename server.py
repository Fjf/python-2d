# Socket server in python using select function

import socket, select
import encoder
import math

def broadcast_data(server_socket, client_socket, clients, bytes):
    for client in clients:
        if client == server_socket or client == client_socket:
            continue
        client.send(bytes)


def check_collision(clientid, clients):
    decd = encoder.Decoder()
    decd.addData(player_coordinates[clientid])
    decd.processData()
    _, clientx, clienty, clientscore = decd.getData()
    for id in player_coordinates:
        if clientid == id:
            continue

        decd.addData(player_coordinates[id])
        if decd.processData():
            _, x, y, score = decd.getData()
            dist = (x - clientx)**2 + (y - clienty)**2
            if (int(30 + 30 + math.sqrt(score) + math.sqrt(clientscore))/2)**2 > dist:
                # Two players collided
                encd = encoder.Encoder()
                if math.sqrt(score) > math.sqrt(clientscore) - 5:
                    # client lost
                    encd.setDeathData()
                    clients[clientid].send(encd.getBytes())
                    encd.setKillData(clientscore)
                    clients[id].send(encd.getBytes())
                elif math.sqrt(clientscore) > math.sqrt(score) - 5:
                    # client won
                    encd.setDeathData()
                    clients[id].send(encd.getBytes())
                    encd.setKillData(score)
                    clients[clientid].send(encd.getBytes())



if __name__ == "__main__":

    clients = {}   # list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 25565

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    clients["-"] = server_socket

    player_data = {}
    player_coordinates = {}

    print("Server started on port " + str(PORT))

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(clients.values(), [], [], 0.01)

        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                try:
                    sockfd, addr = server_socket.accept()

                    clients[addr[1]] = sockfd
                    print("Client (%s, %s) connected" % addr)
                    player_data[addr[1]] = encoder.Decoder()
                    for peername in player_coordinates:
                        sockfd.send(player_coordinates[peername])
                except Exception as e:
                    print(e)

            #Some incoming message from a client
            else:
                # Data received from client, process it
                try:
                    data = sock.recv(RECV_BUFFER)
                    if data and len(data) > 0:
                        clientid = sock.getpeername()[1]
                        player_data[clientid].addData(data)

                        if player_data[clientid].processData():
                            # Set sender of packet in bytearray.
                            player_data[clientid].bytes[2:4] = encoder.intToBytes(clientid, 2)

                            bytes_data = player_data[clientid].getBytes()
                            broadcast_data(server_socket, sock, clients.values(), bytes_data)

                            # Update player coordinates.
                            if encoder.bytesToInt(bytes_data, 4, 5) == encoder.Types.COORDINATE.value:
                                player_coordinates[clientid] = bytes_data
                                check_collision(clientid, clients)


                # client disconnected, so remove from socket list
                except Exception as e:
                    print(e)
                    print(a)
                    del clients[sock.getpeername()[1]]
                    del player_data[sock.getpeername()[1]]
                    sock.close()
                    # broadcast_data(server_socket, None, clients, "msg:%s:Client (%s) is offline" % (addr[1], addr[1]))
                    print("Client (%s, %s) is offline" % addr)
                    continue

    server_socket.close()
