# Socket server in python using select function

import socket, select


def broadcast_data(server_socket, clients, string):
    for client in clients:
        if client == server_socket:
            continue
        client.send(string.encode())

if __name__ == "__main__":

    clients = []    # list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    clients.append(server_socket)

    print("Server started on port " + str(PORT))

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(clients,[],[])

        for sock in read_sockets:

            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                clients.append(sockfd)
                print("Client (%s, %s) connected" % addr)

            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    # echo back the client message
                    if data:
                        stringdata = data.decode('utf-8')
                        stringdata = 'playerdata: ' + stringdata
                        broadcast_data(server_socket, clients, stringdata)

                # client disconnected, so remove from socket list
                except:
                    clients.remove(sock)
                    sock.close()
                    broadcast_data(server_socket, clients, "Client (%s, %s) is offline" % addr)
                    print("Client (%s, %s) is offline" % addr)
                    continue

    server_socket.close()