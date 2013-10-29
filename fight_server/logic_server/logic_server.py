# -*- coding: utf-8 -*-

from twisted.internet import protocol
from twisted.protocols import policies
from twisted.internet.threads import deferToThread
from lib import utils
from lib.rds import logic_server_rds

import msgpack


class LogicServerProtocol(utils.LogMixin, policies.TimeoutMixin, protocol.Protocol):
    """提供给上层接入"""
    pass


class LogicServer(utils.LogMixin, protocol.ServerFactory):
    repstr = "logic"
    protocol = LogicServerProtocol
    rds = logic_server_rds
    unpacker = msgpack.Unpacker()
    cmd_map = {0:"heart",
               1:"register",
               2:"auth",
               3:"disconnect",
               4:"fight"}
    
    def buildProtocol(self, addr):
        p = LogicServerProtocol()
        p.factory = self
        return p
    
    def __str__(self):
        return self.repstr
    
    def waitMsgIn(self):
        """等待接受连接服务器向redis in上发的消息,然后处理"""
        while True:
            _, data = self.rds.popMsgIn(0) # 阻塞队列
            if data:
                self.unpacker.feed(data)
                for cmd, params in self.unpacker:
                    handler = getattr(self, "cmd_%s" % self.cmd_map[cmd])
                    handler(params)
    
    def cmd_heart(self, params):
        self.sendMessage(0, params)
    
    def cmd_register(self, params):
        """注册响应"""
        cmd = 1
        params = [params[0], 1]
        addr = params[0].split(":")[1]
        self.rds.addUser(addr)
        self.sendMessage(cmd, params)
    
    def cmd_auth(self, params):
        """认证响应"""
        cmd = 2
        params = [params[0], 1]
        addr = params[0].split(":")[1]
        if self.rds.isMember(addr):
            params = [params[0], 1]
        else:
            params = [params[0], 2]
        self.sendMessage(cmd, params)
    
    def cmd_disconnect(self, params):
        """广播断开消息,如果redis再设计一个配对结构,就不用广播了
        """
        pass

        
    def cmd_fight(self, params):
        """游戏的主要逻辑处理部分
        @parmas [连接标识, [游戏类型, 目标连接标识, 消息类型, 数据]]"""
        cmd = 4
        addr, game_id, target, msg_id, data = params[0], params[1]
        if msg_id in (1, 3, 5, 6, 7, 9): # 请求XX
            snd_params = [target, [game_id, addr, msg_id, 0]]
            self.sendMessage(cmd, snd_params)
        elif msg_id in (2, 4, 8, 10, 11, 12): # XX响应
            snd_params = [target, [game_id, addr, msg_id, data]]
            self.sendMessage(cmd, snd_params)
        elif msg_id == 13:
            snd_params = [target, [game_id, addr, msg_id, data]]
            self.sendMessage(cmd, snd_params)
            snd_params = [addr, [game_id, target, msg_id, data]]
            self.sendMessage(cmd, snd_params)
            
    def startFactory(self):
        def _errback(reason):
            self.msg("Errback:", repr(reason)) 
        d = deferToThread(self.waitMsgIn)
        d.addErrback(_errback)
        
    def sendMessage(self, cmd, params):
        """把处理的数据发送到redis out队列"""
        self.rds.addMsgOut(cmd, params)
