from twisted.internet.protocol import Protocol, Factory
from twisted.protocols import basic

class Echo(basic.LineReceiver):

	delimiter = "\n"

	def connectionMade(self):
		self.client_ip = self.transport.getPeer().host
		self.client_port = self.transport.getPeer().port
		self.factory.clients.append((self.client_ip, self.client_port))

		self.sendLine("Welcome, there are %d connections currently" %
			(len(self.factory.clients),))
		print "New connection from {}:{}".format(
			self.client_ip, self.client_port)

	def lineReceived(self, line):
		self.sendLine(line)
		if(line.rstrip() != ''):
			print "[%s:%s] %s" % (self.client_ip, self.client_port, line.rstrip())

	def connectionLost(self, reason):
		self.factory.clients.remove((self.client_ip, self.client_port))
		print "{}:{} has disconnected".format(self.client_ip, self.client_port)


class EchoFactory(Factory):
	protocol = Echo
	def __init__(self):
		self.clients = []

if __name__ == '__main__':
	method = raw_input("select or epoll?: ")
	if(method.lower() == "epoll"):
		from twisted.internet import epollreactor
		epollreactor.install()
	from twisted.internet import reactor

	reactor.listenTCP(8005, EchoFactory())
	reactor.run()
