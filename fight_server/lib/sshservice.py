# -*- coding: utf-8 -*-
from twisted.application import strports
from twisted.conch import manhole, manhole_ssh
from twisted.conch.insults import insults
from twisted.cred import portal, checkers

class chainedProtocolFactory:
    def __init__(self, namespace):
        self.namespace = namespace

    def __call__(self):
        return insults.ServerProtocol(manhole.ColoredManhole, self.namespace)

def makeSSHService(listen, passwd, namespace=None):
    namespace = namespace or {}
    checker = checkers.FilePasswordDB(passwd)
    sshRealm = manhole_ssh.TerminalRealm()
    sshRealm.chainedProtocolFactory = chainedProtocolFactory(namespace)
    sshPortal = portal.Portal(sshRealm, [checker])
    sshFactory = manhole_ssh.ConchFactory(sshPortal)
    sshService = strports.service("tcp:%d" % listen, sshFactory)
    return sshService
