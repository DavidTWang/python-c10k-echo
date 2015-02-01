import SocketServer
from threading import Thread

# class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
# 	pass

# class service(SocketServer.BaseRequestHandler):
# 	def handle(self):
# 		data = 'dummy'
# 		print "Client connected with ", self.client_address
# 		while len(data):
# 			data = self.request.recv(1024)
# 			self.request.send(data)

# 		print "Client exited"
# 		self.request.close()

class ThreadedTCPServer():
	def handle(self):
		self.data = self.request.recv(1024).strip()
		print "{} wrote: ".format(self.client_address[0])
		print self.data
		self.request.sendall(self.data_upper())


if __name__ == '__main__':
	HOST = "localhost"
	PORT = 8005

	server = SocketServer.TCPServer((HOST, PORT), ThreadedTCPServer)
	server.serve_forever()