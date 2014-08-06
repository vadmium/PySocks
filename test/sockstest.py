import sys
sys.path.append("..")
import socks
import socket
import unittest
import subprocess
from os import getenv

PY3K = sys.version_info[0] == 3

if PY3K:
    import urllib.request as urllib2
else:
    import sockshandler
    import urllib2

class PythonServerTest(unittest.TestCase):
    def setUp(self):
        args = (getenv("PYTHON2", "python2"), self.server_script)
        self.server = subprocess.Popen(args, stdout=subprocess.PIPE,
            universal_newlines=True)
        try:
            msg = self.server.stdout.readline()
            if not msg.startswith("Running "):
                raise ValueError(msg)
            self.server.stdout.close()
        except:
            PythonServerTest.tearDown(self)
            raise
    
    def tearDown(self):
        self.server.stdout.close()
        self.server.terminate()
        self.server.wait()

class HttpTest(PythonServerTest):
    proxy = (socks.HTTP, "127.0.0.1", 8081)
    server_script = "httpproxy.py"
class Socks4Test(PythonServerTest):
    proxy = (socks.SOCKS4, "127.0.0.1", 1080)
    server_script = "socks4server.py"

class Socks5Test(unittest.TestCase):
    proxy = (socks.SOCKS5, "127.0.0.1", 1081)

def raw_HTTP_request():
    req = "GET /ip HTTP/1.1\r\n"
    req += "Host: ifconfig.me\r\n"
    req += "User-Agent: Mozilla\r\n"
    req += "Accept: text/html\r\n"
    req += "\r\n"
    return req.encode()

def socket_test(self):
    s = socks.socksocket()
    s.set_proxy(*self.proxy)
    s.connect(("ifconfig.me", 80))
    s.sendall(raw_HTTP_request())
    status = s.recv(2048).splitlines()[0]
    self.assertTrue(status.startswith(b"HTTP/1.1 200"))
class SocketHttpTest(HttpTest):
    runTest = socket_test
class SocketSocks4Test(Socks4Test):
    runTest = socket_test
class SocketSocks5Test(Socks5Test):
    runTest = socket_test

class Socks5ConnectTimeoutTest(unittest.TestCase):
    def runTest(self):
        s = socks.socksocket()
        s.settimeout(0.0001)
        s.set_proxy(socks.SOCKS5, "8.8.8.8", 80)
        try:
            s.connect(("ifconfig.me", 80))
        except socks.ProxyConnectionError as e:
            self.assertEqual("timed out", str(e.socket_err))
        else:
            self.fail("ProxyConnectionError not raised")

class Socks5TimeoutTest(Socks5Test):
    def runTest(self):
        s = socks.socksocket()
        s.settimeout(0.0001)
        s.set_proxy(*self.proxy)
        try:
            s.connect(("ifconfig.me", 4444))
        except socks.GeneralProxyError as e:
            self.assertEqual("timed out", str(e.socket_err))
        else:
            self.fail("GeneralProxyError not raised")


class SocketSocks5AuthTest(Socks5Test):
    def runTest(self):
        # TODO: add support for this test. Will need a better SOCKS5 server.
        s = socks.socksocket()
        s.set_proxy(*self.proxy, username="a", password="b")
        s.connect(("ifconfig.me", 80))
        s.sendall(raw_HTTP_request())
        status = s.recv(2048).splitlines()[0]
        self.assertTrue(status.startswith(b"HTTP/1.1 200"))

def socket_ip_test(self):
    s = socks.socksocket()
    s.set_proxy(*self.proxy)
    s.connect(("133.242.129.236", 80))
    s.sendall(raw_HTTP_request())
    status = s.recv(2048).splitlines()[0]
    self.assertTrue(status.startswith(b"HTTP/1.1 200"))
class SocketHttpIpTest(HttpTest):
    runTest = socket_ip_test
class SocketSocks4IpTest(Socks4Test):
    runTest = socket_ip_test
class SocketSocks5IpTest(Socks5Test):
    runTest = socket_ip_test

def urllib2_test(self):
    socks.set_default_proxy(*self.proxy)
    socks.wrap_module(urllib2)
    status = urllib2.urlopen("http://ifconfig.me/ip").getcode()
    self.assertEqual(200, status)
class Urllib2HttpTest(HttpTest):
    runTest = urllib2_test
class Urllib2Socks5Test(Socks5Test):
    runTest = urllib2_test

def urllib2_handler_test(self):
    # "unittest.skipIf" not available in Python 2.6
    if PY3K:
        self.skipTest("sockshandler not written for Python 3")

    opener = urllib2.build_opener(sockshandler.SocksiPyHandler(*self.proxy))
    status = opener.open("http://ifconfig.me/ip").getcode()
    self.assertEqual(200, status)
class Urllib2HandlerHttpTest(HttpTest):
    runTest = urllib2_handler_test
class Urllib2HandlerSocks5Test(Socks5Test):
    runTest = urllib2_handler_test

class GlobalOverrideHttpTest(HttpTest):
    def runTest(self):
        socks.set_default_proxy(*self.proxy)
        good = socket.socket
        socket.socket = socks.socksocket
        status = urllib2.urlopen("http://ifconfig.me/ip").getcode()
        socket.socket = good
        self.assertEqual(200, status)

class GlobalOverrideSocks5Test(Socks5Test):
    def runTest(self):
        socks.set_default_proxy(*self.proxy)
        good = socket.socket
        socket.socket = socks.socksocket
        status = urllib2.urlopen("http://ifconfig.me/ip").getcode()
        socket.socket = good
        self.assertEqual(200, status)
        host = self.proxy[1]
        self.assertEqual(host, socks.get_default_proxy()[1].decode())


if __name__ == "__main__":
    unittest.main()
