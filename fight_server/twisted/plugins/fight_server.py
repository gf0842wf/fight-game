# -*- coding: utf-8 -*-

from link_server import settings
from link_server.share import link_server_share
from logic_server.share import logic_server_share
from twisted.application import internet, service
from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.python.reflect import namedAny
from lib import utils, sshservice
from zope.interface.declarations import implements

import link_server.settings
import logic_server.settings

class Options(usage.Options):
    optParameters = [
        ["settings", "s", "fight_server", "settings module."],
    ]

class ServiceMaker(service.MultiService):
    implements(IServiceMaker, IPlugin)

    tapname = "fight_server"
    description = "Fight Server."
    options = Options

    def makeService(self, options):
        utils.merge_settings(link_server.settings, namedAny("settings." + options["settings"]))
        utils.dump_settings(link_server.settings)
        utils.merge_settings(logic_server.settings, namedAny("settings." + options["settings"]))
        utils.dump_settings(logic_server.settings)

        link_server_share.init(link_server.settings)
        logic_server_share.init(logic_server.settings)

        internet.TCPServer(link_server.settings.TCP_PORT, link_server_share.dev_tcp_svr)\
            .setServiceParent(self)

#         internet.UDPServer(settings.UDP_PORT, link_server_share.dev_udp_svr)\
#             .setServiceParent(self)

        internet.TCPServer(logic_server.settings.TCP_PORT, logic_server_share.dev_tcp_svr)\
            .setServiceParent(self)
                        
        sshservice.makeSSHService(link_server.settings.SSH_PORT, settings.SSH_PASSWD)\
            .setServiceParent(self)

        return self

servic_maker = ServiceMaker()