# Socket server in python using select function

import socket, select
import encoder

def broadcast_data(server_socket, client_socket, clients, bytes):
    for client in clients:
        if client == server_socket or client == client_socket:
            continue
        client.send(bytes)

if __name__ == "__main__":

    clients = []    # list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 25565

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    clients.append(server_socket)

    player_data = {}
    old_player_data = {}

    print("Server started on port " + str(PORT))

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(clients, [], [], 0.01)

        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                try:
                    sockfd, addr = server_socket.accept()
                    clients.append(sockfd)
                    print("Client (%s, %s) connected" % addr)
                    player_data[addr[1]] = encoder.Decoder()
                    for peername in old_player_data:
                        sockfd.send(old_player_data[peername])
                except Exception as e:
                    print(e)

            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    # echo back the client message
                    if data and len(data) > 0:

                        player_data[sock.getpeername()[1]].addData(data)

                        if player_data[sock.getpeername()[1]].processData():

                            # Set sender of packet in bytestream.
                            player_data[sock.getpeername()[1]].bytes[2:4] = encoder.intToBytes(sock.getpeername()[1], 2)

                            bytes_data = player_data[sock.getpeername()[1]].getBytes()
                            broadcast_data(server_socket, sock, clients, bytes_data)

                            old_player_data[sock.getpeername()[1]] = bytes_data


                # client disconnected, so remove from socket list
                except Exception as e:
                    print(e)
                    clients.remove(sock)
                    player_data[sock.getpeername()[1]] = ""
                    sock.close()
                    # broadcast_data(server_socket, None, clients, "msg:%s:Client (%s) is offline" % (addr[1], addr[1]))
                    print("Client (%s, %s) is offline" % addr)
                    continue

    server_socket.close()
