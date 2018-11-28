import os
import platform
import socket
import threading


class Server:

    def __init__(self, host, port, q):
        
        if platform.system() == "Windows":
            
            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Bind the socket to the port
            server_address = ("127.0.0.1", 10000)
            print('starting up on {} port {}'.format(server_address[0], server_address[1]))
            self.sock.bind(server_address)
            
        else:
            server_address = "./uds_socket"
    
            # Make sure the socket does not already exist
            try:
                os.unlink(server_address)
            except OSError:
                if os.path.exists(server_address):
                    raise
    
            # Create a UDS socket
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

            # Bind the socket to the address
            print('starting up on {}'.format(server_address))
            self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(5)

        self.q = q
        self.client_threads = []
        listener_thread = threading.Thread(target=self.listen_for_clients, args=())
        listener_thread.daemon = True
        listener_thread.start()

    def listen_for_clients(self):
        print("Listening...")

        while True:
            client, addr = self.sock.accept()
            # print("Accepted Connection from: {}: {}".format(addr[0], addr[1]))
            t = threading.Thread(target=self.data_sender, args=())
            self.client_threads.append((t, client, addr))
            t.daemon = True
            t.start()

    def data_sender(self):
        while True:
            try:
                while True:
                    data = str(self.q.get()) + ','
                    for client_thread, client, addr in self.client_threads:
                        # print("Sending {} to {}".format(data, addr), file=sys.stderr)
                        client.send(data.encode())
            except:
                return 
