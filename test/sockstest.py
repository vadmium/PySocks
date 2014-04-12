import sys
sys.path.append("..")
import socks
import socket
import unittest

PY3K = sys.version_info[0] == 3

if PY3K:
    import urllib.request as urllib2
else:
    import sockshandler
    import urllib2

def raw_HTTP_request():
    req = "GET /ip HTTP/1.1\r\n"
    req += "Host: ifconfig.me\r\n"
    req += "User-Agent: Mozilla\r\n"
    req += "Accept: text/html\r\n"
    req += "\r\n"
    return req.encode()

class Tests(unittest.TestCase):
    def test_socket_HTTP(self):
        s = socks.socksocket()
        s.set_proxy(socks.HTTP, "127.0.0.1", 8081)
        s.connect(("ifconfig.me", 80))
        s.sendall(raw_HTTP_request())
        status = s.recv(2048).splitlines()[0]
        self.assertTrue(status.startswith(b"HTTP/1.1 200"))

    def test_socket_SOCKS4(self):
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS4, "127.0.0.1", 1080)
        s.connect(("ifconfig.me", 80))
        s.sendall(raw_HTTP_request())
        status = s.recv(2048).splitlines()[0]
        self.assertTrue(status.startswith(b"HTTP/1.1 200"))

    def test_socket_SOCKS5(self):
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, "127.0.0.1", 1081)
        s.connect(("ifconfig.me", 80))
        s.sendall(raw_HTTP_request())
        status = s.recv(2048).splitlines()[0]
        self.assertTrue(status.startswith(b"HTTP/1.1 200"))

    def test_SOCKS5_connect_timeout(self):
        s = socks.socksocket()
        s.settimeout(0.0001)
        s.set_proxy(socks.SOCKS5, "8.8.8.8", 80)
        try:
            s.connect(("ifconfig.me", 80))
        except socks.ProxyConnectionError as e:
            self.assertEqual("timed out", str(e.socket_err))
        else:
            self.fail("ProxyConnectionError not raised")

    def test_SOCKS5_timeout(self):
        s = socks.socksocket()
        s.settimeout(0.0001)
        s.set_proxy(socks.SOCKS5, "127.0.0.1", 1081)
        try:
            s.connect(("ifconfig.me", 4444))
        except socks.GeneralProxyError as e:
            self.assertEqual("timed out", str(e.socket_err))
        else:
            self.fail("GeneralProxyError not raised")


    def test_socket_SOCKS5_auth(self):
        # TODO: add support for this test. Will need a better SOCKS5 server.
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, "127.0.0.1", 1081,
            username="a", password="b")
        s.connect(("ifconfig.me", 80))
        s.sendall(raw_HTTP_request())
        status = s.recv(2048).splitlines()[0]
        self.assertTrue(status.startswith(b"HTTP/1.1 200"))

    def test_socket_HTTP_IP(self):
        s = socks.socksocket()
        s.set_proxy(socks.HTTP, "127.0.0.1", 8081)
        s.connect(("133.242.129.236", 80))
        s.sendall(raw_HTTP_request())
        status = s.recv(2048).splitlines()[0]
        self.assertTrue(status.startswith(b"HTTP/1.1 200"))

    def test_socket_SOCKS4_IP(self):
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS4, "127.0.0.1", 1080)
        s.connect(("133.242.129.236", 80))
        s.sendall(raw_HTTP_request())
        status = s.recv(2048).splitlines()[0]
        self.assertTrue(status.startswith(b"HTTP/1.1 200"))

    def test_socket_SOCKS5_IP(self):
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, "127.0.0.1", 1081)
        s.connect(("133.242.129.236", 80))
        s.sendall(raw_HTTP_request())
        status = s.recv(2048).splitlines()[0]
        self.assertTrue(status.startswith(b"HTTP/1.1 200"))

    def test_urllib2_HTTP(self):
        socks.set_default_proxy(socks.HTTP, "127.0.0.1", 8081)
        socks.wrap_module(urllib2)
        status = urllib2.urlopen("http://ifconfig.me/ip").getcode()
        self.assertEqual(200, status)

    def test_urllib2_SOCKS5(self):
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1081)
        socks.wrap_module(urllib2)
        status = urllib2.urlopen("http://ifconfig.me/ip").getcode()
        self.assertEqual(200, status)

    def test_urllib2_handler_HTTP(self):
        if PY3K:
            self.skipTest("sockshandler not written for Python 3")
        opener = urllib2.build_opener(sockshandler.SocksiPyHandler(socks.HTTP, "127.0.0.1", 8081))
        status = opener.open("http://ifconfig.me/ip").getcode()
        self.assertEqual(200, status)

    def test_urllib2_handler_SOCKS5(self):
        if PY3K:
            self.skipTest("sockshandler not written for Python 3")
        opener = urllib2.build_opener(sockshandler.SocksiPyHandler(socks.SOCKS5, "127.0.0.1", 1081))
        status = opener.open("http://ifconfig.me/ip").getcode()
        self.assertEqual(200, status)

    def test_global_override_HTTP(self):
        socks.set_default_proxy(socks.HTTP, "127.0.0.1", 8081)
        good = socket.socket
        socket.socket = socks.socksocket
        status = urllib2.urlopen("http://ifconfig.me/ip").getcode()
        socket.socket = good
        self.assertEqual(200, status)

    def test_global_override_SOCKS5(self):
        host = "127.0.0.1"
        socks.set_default_proxy(socks.SOCKS5, host, 1081)
        good = socket.socket
        socket.socket = socks.socksocket
        status = urllib2.urlopen("http://ifconfig.me/ip").getcode()
        socket.socket = good
        self.assertEqual(200, status)
        self.assertEqual(host, socks.get_default_proxy()[1].decode())


if __name__ == "__main__":
    unittest.main()
