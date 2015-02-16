import select, socket, sys

HOST = "localhost"
PORT = 8005
BUFFER_SIZE = 256
CONNECTIONS = 5

def echo(connection, address):
	data = connection.recv(BUFFER_SIZE)
	if(data != ""):
		print "Received: %s from %s" % (data, address)
		connection.sendall(data)
	# connection.close()

def select_handling(server):
	try:
		clients = [server]
		max_concurrent_clients = 0

		while(1):
			max_concurrent_clients = max(max_concurrent_clients, len(clients)) - 1
			readList, writeList, exceptions = select.select(clients, [], [])

			# For each socket ready to be read
			for sockets in readList:
				# Ready to accept another client
				if(sockets == server):
					while(1):
						try:
							conn, address = server.accept()
							conn.setblocking(0)
							clients.append(conn)
						except:
							break
				# Echo data from a queued client
				else:
					# clients.remove(sockets)
					echo(sockets, sockets.getpeername())
	finally:
		for sockets in readList:
			sockets.close()
		print "\nMax concurrent clients: {}".format(max_concurrent_clients)

def epoll_handling(server):
	client_socks = {}
	# Read-only flags for connections
	conn_flags = (select.EPOLLIN | select.EPOLLET | select.EPOLLERR | select.EPOLLHUP)
	max_concurrent_clients = 0

	epoll = select.epoll()
	# Register read & edge-trigger descriptor
	epoll.register(server, select.EPOLLIN | select.EPOLLET)

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
							client_socks[conn.fileno()] = conn
							epoll.register(conn, conn_flags)
						except:
							break
				# Handling inputs from clients
				elif(flag & select.EPOLLIN):
					# epoll.unregister(fd)
					echo(client_socks[fd], client_socks[fd].getpeername())

				# Handling errors or holdups
				elif(flag & select.EPOLLERR or flag & select.EPOLLHUP):
					epoll.unregister(fd)
					client_socks[fd].close
	finally:
		print "\nMax concurrent clients: {}".format(max_concurrent_clients)


def main():

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((HOST, PORT))
	server.setblocking(0)

	method = raw_input("Select or epoll?: ").lower()

	try:
		server.listen(CONNECTIONS)
		if(method == "select"):
			select_handling(server)
		elif(method == "epoll"):
			epoll_handling(server)
	except KeyboardInterrupt:
		pass
	finally:
		print "Server shutting down..."
		server.close()

if __name__ == '__main__':
	main()