from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor, defer
from twisted.protocols import basic
from random import uniform
from time import sleep

class Echo(basic.LineReceiver):

	def lineReceived(self, line):
		if(line.rstrip() != ''):
			print "Server reply:", line.rstrip()

	def connectionMade(self):
		self.factory.clients += 1
		self.client_id = self.factory.clients
		print "Client #%d has connected" % self.client_id
		self.sendLine('')
		self.setupMessageLoop(self.factory.repeatCount)
		reactor.callLater(uniform(5.1, 8), self.closeConnection)

	def setupMessageLoop(self, loopRange):
		msg = "Client %d: %s" % (self.client_id, self.factory.message)
		for x in range(loopRange):
			reactor.callLater(uniform(0.0,5.0), self.sendMessages, msg)

	def sendMessages(self, msg):
		print "Sending to server: %s" % msg
		self.sendLine(msg)

	def closeConnection(self):
		self.transport.loseConnection()
		print "Client %d has disconnected" % self.client_id
		self.factory.clients -= 1
		if not self.factory.clients:
			reactor.stop()
	
class EchoClientFactory(ClientFactory):

	protocol = Echo

	def __init__(self, message):
		self.message = message
		self.repeatCount = 1
		self.clients = 0

	def clientConnectionFailed(self, connector, reason):
		print "Connection Failed"
		reactor.stop()

def main():
	port = 8005
	host = raw_input("Server IP: ")
	clientAmt = int(raw_input("How many clients?: "))
	message = raw_input("Message to repeat: ")

	factory = EchoClientFactory(message)

	for i in range(clientAmt):
		reactor.connectTCP(host, port, factory)
	reactor.run()

if __name__ == '__main__':
	main()