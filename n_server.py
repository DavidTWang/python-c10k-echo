import select, socket, sys, logging

HOST = "localhost"
PORT = 8005
BUFFER_SIZE = 1024
CONNECTIONS = 5
logging.basicConfig(filename='server.log', filemode='w', format='[%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
dataSent = {}
dataRecv = {}


def echo(connection, address, clientID):
	global dataRecv
	global dataSent

	data = connection.recv(BUFFER_SIZE).rstrip('/n')
	if(data != ""):
		dataRecv[address[0]] += len(data)
		# print "[%s]Received: %s from %s" % (clientID, data, address)
		connection.sendall(data)
		dataSent[address[0]] += len(data)
	# connection.close()

# def select_handling(server):

# 	clientID = 0

# 	try:
# 		clients = [server]
# 		max_concurrent_clients = 0

# 		while(1):
# 			max_concurrent_clients = max(max_concurrent_clients, len(clients)) - 1
# 			readList, writeList, exceptions = select.select(clients, [], [])

# 			# For each socket ready to be read
# 			for sockets in readList:
# 				# Ready to accept another client
# 				if(sockets == server):
# 					while(1):
# 						try:
# 							conn, address = server.accept()
# 							conn.setblocking(0)
# 							clients.append(conn)
# 							clientID += 1
# 						except:
# 							break
# 				# Echo data from a queued client
# 				else:
# 					# clients.remove(sockets)
# 					echo(sockets, sockets.getpeername(), clientID)
# 	finally:
# 		for sockets in readList:
# 			sockets.close()
# 		print "\nMax concurrent clients: {}".format(max_concurrent_clients)

def epoll_handling(server, trigger):
	global dataRecv
	global dataSent
	client_socks = {}
	max_concurrent_clients = 0
	epoll = select.epoll()

	if(trigger == "edge"):
		# Register read & edge-trigger descriptor
		epoll.register(server.fileno(), select.EPOLLIN | select.EPOLLET)
		# Read-only flags for connections
		conn_flags = (select.EPOLLIN | select.EPOLLET | select.EPOLLERR | select.EPOLLHUP)
	else:
		# Register read descriptor
		epoll.register(server.fileno(), select.EPOLLIN)
		# Read-only flags for connections
		conn_flags = (select.EPOLLIN | select.EPOLLERR | select.EPOLLHUP)

	client_id = 0

	try:
		while(1):
			max_concurrent_clients = max(max_concurrent_clients, len(client_socks))
			events = epoll.poll()
			for fd, flag in events:
				# "Readable" server socket ready to accept a client
				if(fd == server.fileno()):
					while(1):
						try:
							conn, address = server.accept()
							conn.setblocking(0)
							epoll.register(conn, conn_flags)

							client_id += 1
							client_socks[conn.fileno()] = [conn, client_id]
							dataSent[address[0]] = 0
							dataRecv[address[0]] = 0
						except: # socket.error
							break
				# Handling inputs from clients
				elif(flag & select.EPOLLIN):
					# epoll.unregister(fd)
					echo(client_socks[fd][0], client_socks[fd][0].getpeername(), client_socks[fd][1])

				# Handling errors or holdups
				elif(flag & select.EPOLLERR or flag & select.EPOLLHUP):
					epoll.unregister(fd)
					client_socks[fd][0].close
	except:
		print "Error: ", sys.exc_info()[0]
	finally:
		epoll.unregister(server)
		print "\nMax concurrent clients: {}".format(max_concurrent_clients)
		print "Client list: "
		logging.info("Client list: ")
		for clients in dataRecv.keys():
			print clients
			logging.info(clients)
		for ip, r_data in dataRecv.iteritems():
			print "Received %s bytes from %s" % (r_data, ip)
			logging.info("Received %s bytes from %s" % (r_data, ip))
		for ip, s_data in dataSent.iteritems():
			print "Sent %s bytes to %s" % (s_data, ip)
			logging.info("Sent %s bytes to %s" % (s_data, ip))


def main():

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((HOST, PORT))
	server.setblocking(0)

	method = raw_input("Level-trigger[0] or Edge-trigger[1]?: ").lower()

	try:
		server.listen(socket.SOMAXCONN)
		if(method.lower() == "level" or method == "0"):
			print "Starting level-triggered epoll server..."
			epoll_handling(server, "level")
		elif(method.lower() == "edge" or method == "1"):
			print "Starting edge-triggered epoll server..."
			epoll_handling(server, "edge")
	except KeyboardInterrupt:
		pass
	finally:
		print "Server shutting down..."
		server.close()

if __name__ == '__main__':
	main()
