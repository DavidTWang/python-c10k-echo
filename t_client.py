import socket

HOST = raw_input("Server IP: ")
PORT = 8005

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

message = "temp"
while(message != "exit"):
	message = raw_input("Enter message: ")
	sock.sendall(message)
	response = sock.recv(1024)
	print "Received: {}".format(response)

sock.close()