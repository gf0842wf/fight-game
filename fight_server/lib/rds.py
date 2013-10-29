from redis import client
from lib import utils

import link_server.settings
import logic_server.settings
import msgpack

class ServerRds(utils.LogMixin):
    def __init__(self, repstr, settings):
        self.repstr = repstr
        self.settings = settings
        try:
            self.r = client.StrictRedis.from_url(self.settings.MSG_REDIS)
        except Exception as e:
            self.msg("Redis Error:", self.settings.SERVER_NAME, repr(e))
    
    def __str__(self):
        return self.repstr

    def init(self):
        for k in self.r.keys():
            if k.find("fight_link_server:%s:" % self.settings.SERVER_NAME) != -1:
                self.r.delete(k)
                
    def _dump(self, value):
        return msgpack.packb(value)
            
class LinkServerRds(ServerRds):
    def __init__(self):
        ServerRds.__init__(self, "link redis", link_server.settings)
    
    def addMsgIn(self, cmd, params):
        k = self.settings.MSG_IN
        data = [cmd, params]
        vaule = self._dump(data)
        self.r.rpush(k, vaule)
    
    def popMsgOut(self, timeout):
        k = self.settings.MSG_OUT
        return self.r.blpop(k, timeout)


class LogicServerRds(ServerRds):
    def __init__(self):
        ServerRds.__init__(self, "logic redis", logic_server.settings)
        
    def addUser(self, addr):
        k = self.settings.MSG_USER
        self.r.sadd(k, addr)
        
    def isMember(self, addr):
        k = self.settings.MSG_USER
        return self.r.sismember(k, addr)
    
    def addMsgOut(self, cmd, params):
        k = self.settings.MSG_OUT
        data = [cmd, params]
        vaule = self._dump(data)
        self.r.rpush(k, vaule)
        
    def popMsgIn(self, timeout):
        k = self.settings.MSG_IN
        return self.r.blpop(k, timeout)
    
    
link_server_rds = LinkServerRds()
logic_server_rds = LogicServerRds()