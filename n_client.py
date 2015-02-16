import select, socket, sys, time, signal, threading, timeit
from random import uniform
from multiprocessing.dummy import Pool

HOST = "127.0.0.1"
PORT = 8005
BUFFER_SIZE = 256

def echo_client(clientID, message, repeat):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	client_socket.connect((HOST, PORT))

	for i in range(0, repeat):
		time.sleep(uniform(0.0, 2.0))
		client_socket.sendall(message)
		print "Sent: %s" % message
		response = client_socket.recv(BUFFER_SIZE)
		print "Received: %s" % response

	# client_socket.close()

	# echo(client_socket, message)
	# if(repeat > 1):
		# for i in range(0, repeat-1):
			# threading.Timer(2.0, echo, args=[client_socket, message]).start()

	# socket.close()

def main():
	clientNum = int(raw_input("Number of clients to use: "))
	# workerNum = int(raw_input("Number of worker processes: "))
	# workers = Pool(workerNum)

	print("If input is int, then a string of that length will be sent")
	print("If input is string, then it will be sent as it is")
	data = raw_input("Enter the data to send: ")
	repeat = int(raw_input("Amount of times to send it: "))

	if(data.isdigit()):
		data = "." * int(data)

	# for i in xrange(clientNum):
	# 	workers.apply_async(client, args=(i,data,repeat,))
	# workers.close()
	# workers.join()
	clients = []

	for i in xrange(clientNum):
		clientThread = threading.Thread(target=echo_client, args=[i,data,repeat,])
		clientThread.start()
		clients.append(clientThread)

	for client in clients:
		client.join()

if __name__ == '__main__':
	main()