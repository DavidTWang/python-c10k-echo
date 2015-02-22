import threading
import SocketServer
import socket
import logging

logging.basicConfig(filename='server_MT.log', filemode='w', format='[%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
BUFFER_SIZE = 2048
HOST = "localhost"
clientsInfo = {}

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

	def handle(self):
		current_thread = threading.current_thread().name
		ip = self.client_address[0]
		port = self.client_address[1]
		data = "-"
		# print "New Connection from: {}:{} on thread {}".format(ip, port, current_thread)

		while(data != ""):
			dataRecv = 0
			dataSent = 0
			data = self.request.recv(BUFFER_SIZE)
			if(data != ""):
				print data, port
				dataRecv = len(data)
				# print "{} sent: {}".format(current_thread, data)
				self.request.sendall(data)
				dataSent = len(data)
				if(clientsInfo.get(ip) is None):
					clientsInfo[ip] = [dataRecv, dataSent]
				else:
					clientsInfo[ip][0] += dataRecv
					clientsInfo[ip][1] += dataSent
		# clientsInfo[ip] = [dataRecv, dataSent]
		# print "{} disconnected".format(current_thread)

if __name__ == '__main__':
	port = int(raw_input("Enter port: "))

	SocketServer.ThreadingTCPServer.allow_reuse_address = True
	try:
		server = SocketServer.ThreadingTCPServer((HOST, port), ThreadedTCPRequestHandler)
		print "Server started..."
		server.serve_forever()
		print "Server loop running in thread: ", threading.current_thread()
	except KeyboardInterrupt:
		pass
	finally:
		server.shutdown()
		print "\nClient list (hostname)"
		logging.info("Client list (hostname)")
		for ip, totals in clientsInfo.iteritems():
			print "Host:", ip
			print "Received: %s, Sent: %s" % (totals[0], totals[1])
			logging.info("Host: %s" % ip)
			logging.info("Received: %s, Sent: %s" % (totals[0], totals[1]))


