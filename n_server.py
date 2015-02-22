import select, socket, sys, logging, resource

HOST = "localhost"
PORT = 8005
BUFFER_SIZE = 2048
CONNECTIONS = 5
logging.basicConfig(filename='server.log', filemode='w', format='[%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
dataSent = {}
dataRecv = {}


def echo(connection, address, clientID="*"):
	global dataRecv
	global dataSent

	# Receive data, trim trailing newline for easier analysis (else it's 1 extra byte)
	data = connection.recv(BUFFER_SIZE).rstrip('/n')
	if(data != ""):
		print "[%s]Received: %s from %s" % (clientID, data, address)
		dataRecv[address[0]] += len(data)
		connection.sendall(data)
		dataSent[address[0]] += len(data)

def set_rlimit(limit=131072):
	print "rLimit before:", resource.getrlimit(resource.RLIMIT_NOFILE)
	resource.setlimit(resource.RLIMIT_NOFILE, (limit, limit))
	print "rLimit after:", resource.getrlimit(resource.RLIMIT_NOFILE)

def select_handling(server):

	try:
		clientID = 0
		clients = [server]
		clientList = {}
		max_concurrent_clients = 0

		while(1):
			max_concurrent_clients = max(max_concurrent_clients, len(clients)) - 1
			readList, writeList, exceptions = select.select(clients, [], [])

			# For each socket ready to be read
			for sockets in readList:
				# Ready to accept another client
				if(sockets == server):
					try:
						conn, address = server.accept()
						conn.setblocking(0)
						clients.append(conn)
						clientID += 1
						if(dataSent[address[0]] is None):
								pass
					except KeyError:
						dataSent[address[0]] = 0
						dataRecv[address[0]] = 0
				# Echo data from a queued client
				else:
					# clients.remove(sockets)
					echo(sockets, sockets.getpeername())
	finally:
		for sockets in readList:
			sockets.close()
		print "\nMax concurrent clients: {}".format(max_concurrent_clients)
		logging.info("Max concurrent clients: {}".format(max_concurrent_clients))

def epoll_handling(server, trigger):
	global dataRecv
	global dataSent
	client_socks = {}
	client_id = 0
	max_concurrent_clients = 0
	epoll = select.epoll()

	if(trigger == "edge"):
		# Register read & edge-trigger descriptor
		epoll.register(server.fileno(), select.EPOLLIN | select.EPOLLET)
		# Read-only flags for connections
		conn_flags = (select.EPOLLIN | select.EPOLLET | select.EPOLLERR | select.EPOLLHUP)
	elif(trigger == "level"):
		# Register read descriptor
		epoll.register(server.fileno(), select.EPOLLIN)
		# Read-only flags for connections
		conn_flags = (select.EPOLLIN | select.EPOLLERR | select.EPOLLHUP)

	try:
		while(1):
			max_concurrent_clients = max(max_concurrent_clients, len(client_socks))
			events = epoll.poll()
			for fd, flag in events:
				# "Readable" server socket ready to accept a client
				if(fd == server.fileno()):
					try:
						conn, address = server.accept()
						conn.setblocking(0)
						epoll.register(conn, conn_flags)
						client_id += 1
						client_socks[conn.fileno()] = [conn, client_id]
						if(dataSent[address[0]] is None):
							pass
					except KeyError:
						dataSent[address[0]] = 0
						dataRecv[address[0]] = 0
				# Handling inputs from clients
				elif(flag & select.EPOLLIN):
					echo(client_socks[fd][0], client_socks[fd][0].getpeername(), client_socks[fd][1])

				# Handling errors or holdups
				# This section of code apparently never triggers. It can be considered a placeholder for further testing
				# EPOLLHUP is a part of EPOLLERR, and EPOLLER can only occur during EPOLLIN or EPOLLOUT.
				elif(flag & select.EPOLLERR or flag & select.EPOLLHUP):
					epoll.unregister(fd)
					client_socks[fd][0].close
	except:
		print "\nError: ", sys.exc_info()
	finally:
		epoll.unregister(server)
		print "\nMax concurrent clients: {}".format(max_concurrent_clients)
		logging.info("Max concurrent clients: {}".format(max_concurrent_clients))


def main():

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((HOST, PORT))
	server.setblocking(0)

	method = raw_input("Select[0], LT-Epoll[1], ET-Epoll[2], or adjust rLimit[3]?: ")

	try:
		server.listen(socket.SOMAXCONN)
		if(method.lower() == "select" or method == "0"):
			print "Starting select server..."
			select_handling(server)
		elif(method.lower() == "level" or method == "1"):
			print "Starting level-triggered epoll server..."
			epoll_handling(server, "level")
		elif(method.lower() == "edge" or method == "2"):
			print "Starting edge-triggered epoll server..."
			epoll_handling(server, "edge")
		elif(method.lower() == "rlimit" or method == "3"):
			print "Adjusting rLimit..."
			set_rlimit()
	except KeyboardInterrupt:
		pass
	finally:
		print "Client (hostname) list: "
		logging.info("Client (hostname) list: ")
		for clients in dataRecv.keys():
			print clients
			logging.info(clients)
		for ip, r_data in dataRecv.iteritems():
			print "Received %s bytes from %s" % (r_data, ip)
			logging.info("Received %s bytes from %s" % (r_data, ip))
		for ip, s_data in dataSent.iteritems():
			print "Sent %s bytes to %s" % (s_data, ip)
			logging.info("Sent %s bytes to %s" % (s_data, ip))
		print "\nServer shutting down..."
		server.close()

if __name__ == '__main__':
	main()
