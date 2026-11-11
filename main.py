import socket

def http_get(url: str):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((url, 80))

    client_socket.sendall(bytes(f"GET / HTTP/1.1\r\nHost: {url}\r\nAccept-Language: fr\r\n\r\n", "UTF-8"))

    data = client_socket.recv(1024)
    print(f"Received: {data.decode()}")

    client_socket.close()

http_get("example.com") # 와 서버가 내 요청에 응답해줬어