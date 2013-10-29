# -*- coding: utf-8 -*-

class LogicServerShare(object):
    def init(self, settings):
        from . import logic_server

        self.dev_tcp_svr = logic_server.LogicServer()

logic_server_share = LogicServerShare()