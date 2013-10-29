# -*- coding: utf-8 -*-

import platform                        # 业务服务器端口

TCP_PORT = 6302
SERVER_NAME = platform.node()          # 机器名

# redis 服务器
MSG_REDIS = "redis://127.0.0.1:6379/0"
MSG_USER = "fight_link_server:user"
MSG_IN = "fight_link_server:%s:i" % SERVER_NAME
MSG_OUT = "fight_link_server:%s:o" % SERVER_NAME