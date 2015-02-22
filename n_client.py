import socket, time, threading, timeit, logging
from random import uniform

HOST = "localhost"
PORT = 8005
BUFFER_SIZE = 2048
logging.basicConfig(filename='client.log', filemode='w', format='[%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
total_time = 0

def echo_client(clientID, message, repeat):
	global total_time

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((HOST, PORT))
	dataSent = 0
	dataRecv = 0

	for i in range(0, repeat):
		time.sleep(uniform(0.0, 3.0))

		start_time = timeit.default_timer()
		client_socket.sendall(message)
		dataSent += len(message)

		response = client_socket.recv(BUFFER_SIZE)
		end_time = (timeit.default_timer() - start_time) * 1000
		total_time += end_time
		dataRecv += len(response)
		logging.info("Client %d Message %d RTT: %fms" % (clientID, i+1, end_time))

	logging.info("Client %d finished. Amount sent|recv: %d|%d bytes" % (clientID, dataSent, dataRecv))

def main():
	clientNum = int(raw_input("Number of clients to setup: "))

	print("If input is int, then a string of that length will be sent")
	print("If input is string, then it will be sent as it is")
	data = raw_input("Enter the data to send: ")
	repeat = int(raw_input("Amount of times to send it (per client): "))

	if(data.isdigit()):
		data = "." * int(data)

	clients = []

	for i in xrange(clientNum):
		clientThread = threading.Thread(target=echo_client, args=[i,data,repeat,])
		clientThread.start()
		clients.append(clientThread)

	for client in clients:
		client.join()

	print "Total time used: %0.6fms" % total_time
	logging.info("Total time used: %fms" % total_time)

if __name__ == '__main__':
	main()