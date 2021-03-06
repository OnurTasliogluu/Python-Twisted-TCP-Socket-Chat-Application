from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

class Chat(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.name = None
        self.state = "GETNAME".encode()

    def connectionMade(self):
        self.sendLine("What's your name?".encode())

    def connectionLost(self, reason):
        if self.name in self.users:
            del self.users[self.name]

    def lineReceived(self, line):
        if self.state == "GETNAME".encode():
            self.handle_GETNAME(line)
        else:
            self.handle_CHAT(line)

    def handle_GETNAME(self, name):
        if name in self.users:
            self.sendLine("Name taken, please choose another.".encode())
            return
        self.sendLine("Welcome, %s!".encode() % (name,))
        self.name = name
        self.users[name] = self
        self.state = "CHAT".encode()

    def handle_CHAT(self, message):
        message = "<%s> %s".encode() % (self.name, message)
        for name, protocol in self.users.items():
            if protocol != self:
                protocol.sendLine(message)


class ChatFactory(Factory):

    def __init__(self):
        self.users = {} # maps user names to Chat instances

    def buildProtocol(self, addr):
        return Chat(self.users)


reactor.listenTCP(8123, ChatFactory())
reactor.run()