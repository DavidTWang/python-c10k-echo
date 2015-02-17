import threading
import SocketServer
import socket


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		current_thread = threading.current_thread().name
		ip = self.client_address[0]
		port = self.client_address[1]
		data = "temp"

		print "New Connection from: {}:{} on thread {}".format(ip, port, current_thread)

		while len(data):
			data = self.request.recv(1024)
			if(data != ""):
				print "{} sent: {}".format(current_thread, data)
			self.request.sendall(data)
		# print "{} disconnected".format(current_thread)

# class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
# 	pass

if __name__ == '__main__':
	HOST = "localhost"
	temp = socket.getfqdn()
	port = int(raw_input("Enter port: "))

	SocketServer.ThreadingTCPServer.allow_reuse_address = True
	server = SocketServer.ThreadingTCPServer((HOST, port), ThreadedTCPRequestHandler)
	print temp
	print "Server started..."
	server.serve_forever()
	print "Server loop running in thread: ", threading.current_thread()
	server.shutdown()

