# -*- coding: utf-8 -*-

class LinkServerShare(object):
    def init(self, settings):
        from . import link_server

        self.dev_tcp_svr = link_server.LinkTCPServer()
#         self.dev_udp_svr = link_server.DeviceUDPProtocol()

link_server_share = LinkServerShare()
