#!/usr/bin/env python
from twisted.internet import reactor
from twisted.protocols.socks import SOCKSv4Factory
from sys import stdout

def run_proxy():
    reactor.listenTCP(1080, SOCKSv4Factory("/dev/null"), interface="127.0.0.1")
    stdout.write("Running SOCKS4 proxy server\n")
    stdout.flush()
    
    try:
        reactor.run()
    except (KeyboardInterrupt, SystemExit):
        reactor.stop()

if __name__ == "__main__":
    run_proxy()
