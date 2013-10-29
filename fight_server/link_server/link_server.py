# -*- coding: utf-8 -*-

from . import settings
from twisted.internet import protocol
from twisted.protocols import policies
from twisted.internet.threads import deferToThread
from lib import utils
from lib.rds import link_server_rds

import msgpack

class LinkServerTCPProtocol(utils.LogMixin, policies.TimeoutMixin, protocol.Protocol):
    repstr = "link"
    
    def __str__(self):
        return self.repstr
    
    def connectionMade(self):
        # 建立连接
        self.setTimeout(settings.TCP_CONN_TIMEOUT)
        self.data_timeout = settings.TCP_DATA_TIMEOUT
#         self.local_addr = "%s:%d" % (settings.SERVER_NAME, self.transport.getHost().port)
        self.conn_flag = self.factory.addr
        
        self.factory.addr2clis[self.conn_flag] = self 
        self.msg("Connection Made:", self.conn_flag)

    def connectionLost(self, reason):
        """连接断开发送到redis in 队列"""
        cmd = 3
        params = [self.conn_flag, 1] # 暂时不区分断开类型
        self.factory.rds.addMsgIn(cmd, params)
        # 连接断开
        if self.factory.addr2clis.get(self.conn_flag):
            del self.factory.addr2clis[self.conn_flag]
        self.msg("Connection Lost:", self.conn_flag, reason.getErrorMessage()) 

    def dataReceived(self, data):
        self.setTimeout(self.data_timeout)
        # 收到客户端数据
        self.factory.unpacker.feed(data)
        for cmd, params in self.factory.unpacker:
            self.handler(cmd, params)
    
    def handler(self, cmd, params):
        """添加连接标识后发送到redis in 队列"""
        params = [self.conn_flag] + params
        self.factory.rds.addMsgIn(cmd, params)
        
    def timeoutConnection(self):
        self.msg("Connection Timeout:", self.conn_flag)
        policies.TimeoutMixin.timeoutConnection(self)
    
    def sendMessage(self, addr, data):
        self.transport.write(data)
        self.msg("Send Data:", addr, len(data), utils.strdump(data))    


class LinkTCPServer(utils.LogMixin, protocol.ServerFactory):
    protocol = LinkServerTCPProtocol
    addr2clis = {}
    rds = link_server_rds
    unpacker = msgpack.Unpacker()
    
    def buildProtocol(self, addr):
        p = LinkServerTCPProtocol()
        p.repstr = "TCP:%s:%d" % (addr.host, addr.port)
        p.factory = self
        p.factory.addr = p.repstr
        return p
    
    def waitMsgOut(self):
        """等待接受业务服务器向redis out下发的消息"""
        while True:
            _, data = self.rds.popMsgOut(0) # 阻塞队列
            if data:
                self.unpacker.feed(data)
                for cmd, params in self.unpacker:
                    data = msgpack.packb([cmd, params[1:]]) # 连接服务器下发到客户端不带连接标识
                    self.sendMessage(params[0], data)
    
    def startFactory(self):
        def _errback(reason):
            self.msg("Errback:", repr(reason)) 
        d = deferToThread(self.waitMsgOut)
        d.addErrback(_errback)
        
    def sendMessage(self, addr, data):
        """把redis out队列的数据发送到客户端"""
        client = self.addr2clis.get(addr)
        if client:
            client.sendMessage(addr, data)
