import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind(('localhost', 80))

server_socket.listen()

print("Server waiting for connections...")
client_socket, addr = server_socket.accept()
print(f"Connected by {addr}")

data = client_socket.recv(1024)
print(f"Received data: {data.decode()}")
client_socket.sendall(data)

client_socket.close()
server_socket.close()
